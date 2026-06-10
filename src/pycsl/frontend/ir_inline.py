"""inline.md — inlining method calls on module-level global instances.

An IR-level pass between Module 5 (IR emit) and Module 6 (WhyML transpile). It:

  1. **(Phase 2)** inlines each call `g.m(args)` on a module-level global instance `g`,
     splicing method `m`'s body with `self`→`g` and formals→actuals (and freshened
     locals), so the caller's VC contains the real field reads/writes — closing the
     method-call contract gap (A2c) for global receivers.
  2. **(Phase 1)** demotes the `pure` flag on any function that reads or writes a module
     global, so Module 6 emits it as a program `let` rather than a logic `let function`
     (a Why3 logic function cannot depend on mutable global state).
  3. **(Phase 3)** refuses to inline a (directly or mutually) recursive method — a hard
     error — and bounds transitive inlining depth.

No-op when the module declares no object globals (`module_globals` empty/absent), so
emission for every existing program is byte-identical.
"""
import copy
from typing import Any, Dict, List, Optional, Set, Tuple

from errors import PyCSLSemanticError

# Transitive-inlining depth cap (Phase 3): a global method inlining another global
# method … — bounded so the pass always terminates and VCs don't blow up.
_MAX_INLINE_DEPTH = 16


# ----------------------------------------------------------------------------- utils
def _walk_dicts(obj: Any):
    """Yield every dict node in an IR tree (depth-first)."""
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _walk_dicts(v)
    elif isinstance(obj, list):
        for x in obj:
            yield from _walk_dicts(x)


def _touches_global(obj: Any, globals_set: Set[str]) -> bool:
    """True if the IR tree reads or writes a *field* of a module global (`g.field`,
    `g.field <- …`, or — after inlining self→g — a `FieldGet`/`FieldAssign` whose
    `object` is a global name)."""
    for node in _walk_dicts(obj):
        t = node.get("type") or node.get("stmt")
        if t == "Attribute":
            o = node.get("object")
            if (isinstance(o, dict) and o.get("type") == "Var"
                    and o.get("name") in globals_set):
                return True
        elif t in ("FieldGet", "FieldAssign", "FieldAugAssign"):
            if node.get("object") in globals_set:
                return True
    return False


def _method_key(cls: str, method: str) -> str:
    """The function-IR name for class `cls`'s method `method` (Module 5 mangling)."""
    return f"{cls.lower()}__{method}"


def _global_call_target(call: Dict[str, Any], globals_set: Set[str],
                        g_class: Dict[str, str]) -> Optional[str]:
    """If `call` is `g.m(args)` on a module global `g`, return the callee method key
    `<class>__m`; else None."""
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return None
    func = call.get("func")
    if not isinstance(func, str) or "." not in func:
        return None
    recv, _, method = func.partition(".")
    if recv in globals_set and "." not in method:
        return _method_key(g_class[recv], method)
    return None


# --------------------------------------------------------------- recursion detection
def _method_edges(func: Dict[str, Any], names: Set[str], self_cls: str,
                  globals_set: Set[str], g_class: Dict[str, str]) -> Set[str]:
    """Outgoing method-call edges of a function: `self.X` → `<self_cls>__X`, `g.X` →
    `<g_class>__X`, bare `f(...)` → `f` (when those names exist)."""
    out: Set[str] = set()
    for node in _walk_dicts(func.get("body")):
        if node.get("type") != "Call":
            continue
        func_name = node.get("func")
        if not isinstance(func_name, str):
            continue
        if func_name.startswith("self.") and self_cls:
            cand = _method_key(self_cls, func_name[len("self."):])
        elif "." in func_name:
            recv, _, m = func_name.partition(".")
            cand = _method_key(g_class[recv], m) if recv in globals_set else None
        else:
            cand = func_name
        if cand in names:
            out.add(cand)
    return out


def _recursive_methods(funcs: List[Dict[str, Any]], globals_set: Set[str],
                       g_class: Dict[str, str]) -> Set[str]:
    """Names of functions/methods that are (directly or mutually) recursive — i.e. a
    node reachable from itself through method-call edges. Such a method must NOT be
    inlined (it would not terminate); it is verified by contract + `#@ \\variant`."""
    fmap = {f["name"]: f for f in funcs}
    names = set(fmap)
    edges = {
        name: _method_edges(f, names, (f.get("self_type") or "").rstrip(),
                            globals_set, g_class)
        for name, f in fmap.items()
    }

    def reaches_self(start: str) -> bool:
        seen: Set[str] = set()
        stack = list(edges.get(start, ()))
        while stack:
            n = stack.pop()
            if n == start:
                return True
            if n in seen:
                continue
            seen.add(n)
            stack.extend(edges.get(n, ()))
        return False

    return {n for n in names if reaches_self(n)}


# ------------------------------------------------------------------ substitution
def _assigned_locals(stmts: Any) -> Set[str]:
    """Local names a method body binds (Assign/AugAssign/For targets) — freshened on
    inlining so they don't collide with (or capture) the caller's locals."""
    out: Set[str] = set()
    for node in _walk_dicts(stmts):
        s = node.get("stmt")
        if s in ("Assign", "AugAssign", "For") and isinstance(node.get("target"), str):
            out.add(node["target"])
    return out


def _substitute(node: Any, self_name: str, param_map: Dict[str, Any],
                rename: Dict[str, str]) -> Any:
    """Deep-copy `node`, applying, in one pass: a formal `Var`→its actual IR; a method
    local→its freshened name; the `self` receiver→`self_name` in `FieldGet` /
    `FieldAssign` / `FieldAugAssign` objects and in `self.X(...)` call funcs."""
    if isinstance(node, list):
        return [_substitute(x, self_name, param_map, rename) for x in node]
    if not isinstance(node, dict):
        return node
    if node.get("type") == "Var":
        nm = node.get("name")
        if nm in param_map:
            return copy.deepcopy(param_map[nm])
        if nm in rename:
            return {"type": "Var", "name": rename[nm]}
        return dict(node)
    new = {k: _substitute(v, self_name, param_map, rename) for k, v in node.items()}
    t = new.get("type")
    s = new.get("stmt")
    if t == "FieldGet" and new.get("object") == "self":
        new["object"] = self_name
    if s in ("FieldAssign", "FieldAugAssign") and new.get("object") == "self":
        new["object"] = self_name
    if t == "Call" and isinstance(new.get("func"), str):
        fn = new["func"]
        if fn.startswith("self."):
            new["func"] = self_name + fn[len("self"):]   # self.Y -> <self_name>.Y
        elif "." in fn:
            # Freshen local-variable receiver in dotted calls like
            # `entries.append(x)` → `entries__inlN.append(x)`.
            recv_part, _, method_part = fn.partition(".")
            if recv_part in rename:
                new["func"] = f"{rename[recv_part]}.{method_part}"
    if s in ("Assign", "AugAssign", "For") and isinstance(new.get("target"), str):
        if new["target"] in rename:
            new["target"] = rename[new["target"]]
    return new


class _Inliner:
    def __init__(self, funcs, globals_set, g_class, recursive, no_inline=None):
        self.fmap = {f["name"]: f for f in funcs}
        self.globals_set = globals_set
        self.g_class = g_class
        self.recursive = recursive
        # no-inline.md Piece B: methods marked `#@ no_inline` are NOT spliced; their calls
        # are left in place to lower as contract-calls to the verified method.
        self.no_inline = no_inline or set()
        self.counter = 0

    def _fresh(self, base: str) -> str:
        self.counter += 1
        return f"{base}__inl{self.counter}"

    def _expand(self, callee: str, recv: str, args: List[Any],
                result_var: Optional[str]) -> List[Any]:
        """Produce the inlined statement list for `recv.m(args)`. `result_var` (or None
        for a void/statement-position call) receives the method's return value via a
        trailing `Assign`. Raises on a recursive method or a non-tail return."""
        m = self.fmap.get(callee)
        if m is None:
            raise PyCSLSemanticError(
                f"cannot inline call to '{recv}.{callee.split('__')[-1]}': method "
                f"'{callee}' not found.")
        if callee in self.recursive:
            raise PyCSLSemanticError(
                f"cannot inline recursive method '{callee}' on global '{recv}': a "
                f"recursive method is verified by contract + `#@ \\variant`, not by "
                f"inlining (inline.md Phase 3).")
        formals = m.get("formal_params", [])
        if len(args) != len(formals):
            raise PyCSLSemanticError(
                f"cannot inline '{callee}': call passes {len(args)} args, method takes "
                f"{len(formals)}.")
        body = copy.deepcopy(m.get("body", []))
        # Freshen the callee's locals; bind non-trivial actuals to temps (no double-eval
        # / capture); map each formal to its actual (or temp).
        # sorted: _assigned_locals is a set — deterministic __inl<N> numbering
        rename = {loc: self._fresh(loc) for loc in sorted(_assigned_locals(body))}
        pre: List[Any] = []
        param_map: Dict[str, Any] = {}
        for formal, actual in zip(formals, args):
            if isinstance(actual, dict) and actual.get("type") in ("Var", "Number", "Constant", "Bool", "String"):
                param_map[formal] = actual
            else:
                tmp = self._fresh(formal)
                pre.append({"stmt": "Assign", "target": tmp, "value": copy.deepcopy(actual)})
                param_map[formal] = {"type": "Var", "name": tmp}
        body = [_substitute(st, recv, param_map, rename) for st in body]
        # A `return` may appear only as the LAST statement (tail). Mid-body returns
        # would need control-flow duplication — refuse (sound restriction).
        for st in body[:-1] if body else []:
            if isinstance(st, dict) and st.get("stmt") == "Return":
                raise PyCSLSemanticError(
                    f"cannot inline '{callee}' on '{recv}': it has a non-tail `return` "
                    f"(early return / return inside a branch). Verify it by contract.")
        out = list(pre)
        if body and isinstance(body[-1], dict) and body[-1].get("stmt") == "Return":
            ret = body.pop()
            out.extend(body)
            val = ret.get("value")
            if result_var is not None:
                if val is None:
                    raise PyCSLSemanticError(
                        f"cannot inline '{callee}' in expression position: it returns "
                        f"no value.")
                out.append({"stmt": "Assign", "target": result_var, "value": val})
            # a `return None` / bare return in statement position → nothing to bind
        else:
            out.extend(body)
            if result_var is not None:
                raise PyCSLSemanticError(
                    f"cannot inline '{callee}' in expression position: its body does "
                    f"not end in a `return`.")
        return out

    def _hoist_calls_in_expr(self, node: Any, pre: List[Any]) -> Any:
        """Replace every `g.m(args)` call inside expression `node` with a fresh result
        Var, appending the inlining statements (binding that var) to `pre`. Returns the
        rewritten expression."""
        if isinstance(node, list):
            return [self._hoist_calls_in_expr(x, pre) for x in node]
        if not isinstance(node, dict):
            return node
        callee = _global_call_target(node, self.globals_set, self.g_class)
        if callee is not None and callee in self.no_inline:
            # no-inline.md Piece B: a `#@ no_inline` callee — leave the call in place (hoist
            # any nested global calls in its args) so Module6 lowers it as a contract-call.
            new_args = [self._hoist_calls_in_expr(a, pre) for a in node.get("args", [])]
            return {**node, "args": new_args}
        if callee is not None:
            recv = node["func"].partition(".")[0]
            hoisted_args = [self._hoist_calls_in_expr(a, pre) for a in node.get("args", [])]
            res = self._fresh("_inl_res")
            pre.extend(self._expand(callee, recv, hoisted_args, res))
            return {"type": "Var", "name": res}
        return {k: self._hoist_calls_in_expr(v, pre) for k, v in node.items()}

    def inline_stmts(self, stmts: List[Any]) -> List[Any]:
        """Return a new statement list with all global-method calls inlined. Recurses
        into nested suites (If/While/For/Try/Match)."""
        out: List[Any] = []
        for st in stmts:
            if not isinstance(st, dict):
                out.append(st)
                continue
            # Statement-position call `g.m(args)` (return value discarded).
            if st.get("stmt") == "Expr":
                callee = _global_call_target(st.get("value", {}), self.globals_set, self.g_class)
                if callee is not None and callee in self.no_inline:
                    # no-inline.md Piece B: leave a `#@ no_inline` statement-call in place.
                    pre: List[Any] = []
                    new_args = [self._hoist_calls_in_expr(a, pre)
                                for a in st["value"].get("args", [])]
                    out.extend(pre)
                    out.append({**st, "value": {**st["value"], "args": new_args}})
                    continue
                if callee is not None:
                    recv = st["value"]["func"].partition(".")[0]
                    pre: List[Any] = []
                    hoisted_args = [self._hoist_calls_in_expr(a, pre)
                                    for a in st["value"].get("args", [])]
                    out.extend(pre)
                    out.extend(self._expand(callee, recv, hoisted_args, None))
                    continue
            # Recurse into nested suites first.
            st = dict(st)
            for key in ("body", "orelse", "finalbody"):
                if isinstance(st.get(key), list):
                    st[key] = self.inline_stmts(st[key])
            if isinstance(st.get("handlers"), list):
                st["handlers"] = [
                    {**h, "body": self.inline_stmts(h["body"])} if isinstance(h, dict)
                    and isinstance(h.get("body"), list) else h
                    for h in st["handlers"]]
            if isinstance(st.get("cases"), list):
                st["cases"] = [
                    {**c, "body": self.inline_stmts(c["body"])} if isinstance(c, dict)
                    and isinstance(c.get("body"), list) else c
                    for c in st["cases"]]
            # Hoist any global-method call appearing in this statement's expressions.
            pre = []
            new_st = {}
            for k, v in st.items():
                new_st[k] = self._hoist_calls_in_expr(v, pre) if k not in (
                    "body", "orelse", "finalbody", "handlers", "cases") else v
            out.extend(pre)
            out.append(new_st)
        return out


def _check_no_aliasing(funcs: List[Dict[str, Any]], globals_set: Set[str]) -> None:
    """Phase 3 aliasing ban: a module global may be used only as a method receiver
    (`g.m(...)`) or field access (`g.field`) — not bound to a local (`x = g`) nor passed
    as a call argument (`f(g)`), either of which would alias the single global object."""
    for f in funcs:
        for node in _walk_dicts(f.get("body")):
            if (node.get("stmt") == "Assign" and isinstance(node.get("value"), dict)
                    and node["value"].get("type") == "Var"
                    and node["value"].get("name") in globals_set):
                raise PyCSLSemanticError(
                    f"cannot alias module global '{node['value']['name']}' into a local "
                    f"(inline.md Phase 3): a global is a single named object — call its "
                    f"methods or read its fields directly.")
            if node.get("type") == "Call":
                for a in node.get("args", []):
                    if (isinstance(a, dict) and a.get("type") == "Var"
                            and a.get("name") in globals_set):
                        raise PyCSLSemanticError(
                            f"cannot pass module global '{a['name']}' as an argument "
                            f"(inline.md Phase 3): would alias the global; operate on it "
                            f"via its own methods/fields.")


def _inline_calls(funcs: List[Dict[str, Any]], globals_set: Set[str],
                  g_class: Dict[str, str]) -> None:
    recursive = _recursive_methods(funcs, globals_set, g_class)
    no_inline = {f["name"] for f in funcs if f.get("no_inline")}
    inliner = _Inliner(funcs, globals_set, g_class, recursive, no_inline)
    for f in funcs:
        body = f.get("body", [])
        for _ in range(_MAX_INLINE_DEPTH):
            new_body = inliner.inline_stmts(body)
            if new_body == body:
                break
            body = new_body
        else:
            raise PyCSLSemanticError(
                f"inlining depth exceeded ({_MAX_INLINE_DEPTH}) in '{f['name']}' — "
                f"a chain of global method calls too deep to inline (inline.md Phase 3).")
        f["body"] = body


def apply_inline_globals(ir_data: Dict[str, Any]) -> None:
    """Run the inlining pass in place. See module docstring."""
    globals_list = ir_data.get("module_globals", [])
    if not globals_list:
        return
    globals_set = {g["name"] for g in globals_list}
    g_class = {g["name"]: g["class"] for g in globals_list}
    funcs = ir_data.get("functions", [])

    # Phase 3: a module global is a single named object — forbid aliasing it (binding it
    # to a local or passing it as an argument), which would reintroduce the aliasing the
    # one-name model avoids. Checked on the ORIGINAL bodies (before inlining rewrites the
    # `g.m(args)` receivers away).
    _check_no_aliasing(funcs, globals_set)

    # Phase 2/3: inline method calls on globals (recursion-guarded, depth-bounded).
    _inline_calls(funcs, globals_set, g_class)

    # Phase 1: a function that (now) reads/writes a global field is not a pure logic
    # function — demote it so Module 6 emits a program `let` with the inferred effect.
    for f in funcs:
        if (_touches_global(f.get("body"), globals_set)
                or _touches_global(f.get("contracts"), globals_set)):
            f.pop("pure", None)
