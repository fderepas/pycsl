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
        # (#49) ROUTE #169 — a tuple-unpacking bind is a local too. `_assigned_locals` sees
        # only single-name targets, so `a, b = d, d` in the callee kept its spelling and
        # OVERWROTE the caller's `a`: `a = 7; _g.f(100); return a` PROVED `\result == 100`
        # (CPython 7). Freshen those names as well (their `Var` uses are renamed by
        # `_substitute`; the `targets` list is renamed after it).
        _tu169: List[str] = []
        for _n169 in _walk_dicts(body):
            if _n169.get("stmt") == "TupleUnpack" and isinstance(_n169.get("targets"), list):
                for _t169 in _n169["targets"]:
                    if isinstance(_t169, str) and _t169 not in rename and _t169 not in _tu169:
                        _tu169.append(_t169)
        for _t169 in sorted(_tu169):
            rename[_t169] = self._fresh(_t169)
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
        for _n169 in _walk_dicts(body):
            if _n169.get("stmt") == "TupleUnpack" and isinstance(_n169.get("targets"), list):
                _n169["targets"] = [rename.get(_t169, _t169) if isinstance(_t169, str)
                                    else _t169 for _t169 in _n169["targets"]]
        # (#49) ROUTE #169 — A NAME THE CALLEE READS FROM MODULE SCOPE IS CAPTURED BY A
        # CALLER LOCAL OF THE SAME NAME. Only the callee's own binds are freshened; every
        # other identifier in the spliced body keeps its spelling and so resolves in the
        # CALLER's scope. MEASURED: `K = 3` at module level, `def f(self): return K`, and a
        # caller `K = 9; return _g.f()` PROVED `\result == 9` (CPython 3). Refuse when an
        # unfreshened identifier of the spliced body is bound by the caller (a parameter or
        # any assignment/loop/unpack target).
        _cb169 = getattr(self, "caller_binders", set()) or set()
        if _cb169:
            _seen169: Set[str] = set()
            for _n169 in _walk_dicts(body):
                if _n169.get("type") == "Var" and isinstance(_n169.get("name"), str):
                    _seen169.add(_n169["name"])
                for _k169 in ("target", "object"):
                    if isinstance(_n169.get(_k169), str):
                        _seen169.add(_n169[_k169])
                if isinstance(_n169.get("targets"), list):
                    _seen169.update(t for t in _n169["targets"] if isinstance(t, str))
                if _n169.get("type") == "Call" and isinstance(_n169.get("func"), str) \
                        and "." in _n169["func"]:
                    _seen169.add(_n169["func"].partition(".")[0])
            _fresh169 = set(rename.values()) | {
                a.get("name") for a in param_map.values()
                if isinstance(a, dict) and a.get("type") == "Var"}
            _cap169 = sorted(n for n in (_seen169 & _cb169)
                             if n not in _fresh169 and n != recv)
            if _cap169:
                raise PyCSLSemanticError(
                    f"cannot inline '{callee}' on '{recv}': its body refers to "
                    f"{', '.join(repr(n) for n in _cap169)}, which the calling function binds "
                    f"as a local, so the spliced body would read the CALLER's variable instead "
                    f"of the name the method sees (route #169). Rename the local.")
        # A `return` may appear only as the LAST statement (tail). Mid-body returns
        # would need control-flow duplication — refuse (sound restriction).
        for st in body[:-1] if body else []:
            if isinstance(st, dict) and st.get("stmt") == "Return":
                raise PyCSLSemanticError(
                    f"cannot inline '{callee}' on '{recv}': it has a non-tail `return` "
                    f"(early return / return inside a branch). Verify it by contract "
                    f"instead — call the method on a LOCAL instance (`c = C(); c.m()`), "
                    f"which uses its contract at the call site rather than splicing its "
                    f"body. MEASURED in gen #30: adding a contract while KEEPING the "
                    f"module-global receiver does not help, and neither does "
                    f"`#@ \\trusted` — the inliner runs on a global-receiver call "
                    f"regardless of either.")
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
            # (#49) ROUTE #168 — A DISCARDED RETURN VALUE IS STILL EVALUATED. In statement
            # position the tail `return <e>` was popped and `<e>` thrown away, so whatever
            # evaluating it DOES vanished with it: `_g.run()` with `run` returning
            # `self.bumpret()` (a mutator) PROVED `_g.x - a == 0` (CPython 1), and a method
            # `requires self.x != 0` returning `self.x // self.x` PROVED its caller on
            # `_g = C(0)` (CPython ZeroDivisionError). Bind it to a fresh discard local
            # instead: the next fixpoint round inlines any global call inside it, and
            # Module 6 lowers the evaluation with its checks.
            elif (val is not None
                  and not (isinstance(val, dict)
                           and val.get("type") in ("Constant", "NameConstant", "None")
                           and val.get("value") is None)):
                out.append({"stmt": "Assign", "target": self._fresh("_inl_discard"),
                            "value": val})
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
                  g_class: Dict[str, str],
                  rewrite_funcs: Optional[List[Dict[str, Any]]] = None) -> None:
    recursive = _recursive_methods(funcs, globals_set, g_class)
    no_inline = {f["name"] for f in funcs if f.get("no_inline")}
    inliner = _Inliner(funcs, globals_set, g_class, recursive, no_inline)
    # `funcs` (all) populates the inliner's callee map; only `rewrite_funcs`
    # bodies are rewritten in place (defaults to all funcs — 11-1039-spec-10
    # passes the non-trusted subset so emission-dead trusted-stub bodies, whose
    # `g.method()` receivers reference methods the importer never imported, are
    # not walked).
    for f in (rewrite_funcs if rewrite_funcs is not None else funcs):
        # (#49) ROUTE #106 — INLINING DELETED THE CALL, AND WITH IT THE OBLIGATION.
        # A caller declaring `#@ no_exception E` that calls a global-instance method
        # declaring `#@ raises E when P` must discharge `assert { not P }` at the call
        # site — `Module6_WhyMLTranspiler._wrap_call_with_callee_raises_assert` emits
        # exactly that, and routes #100 and #105 extended it to the `self.<m>` and
        # `<recordvar>.<m>` receivers. But that wrap lives at a CALL SITE, and this pass
        # runs EARLIER, on the IR, and SPLICES THE CALLEE BODY IN — so by the time
        # Module 6 looks, there is no call left to wrap.
        #
        # MEASURED at ac2ef23e: `_h = Helper()` then `_h.f(k)` inside a
        # `#@ no_exception ValueError` caller emitted
        #     let caller (k: int) : int
        #       raises { ValueError }            <- Why3 is TOLD it raises
        #     = let _inl_res__inl1 = ref 0 in
        #       if (k < 0) then begin raise ValueError end; ...
        # and PyCSL reported `All contracts formally proven`. CPython `caller(-1)` RAISES.
        # The emitted signature CONTRADICTED the source directive and nothing compared
        # them. It was inlined EVEN WHEN THE CALLEE WAS `\trusted` — the `val` was emitted
        # and never called, so the trust boundary was spliced straight through.
        #
        # >>> A TRANSFORMATION THAT REMOVES A SYNTACTIC FORM REMOVES EVERY OBLIGATION
        # >>> KEYED ON THAT FORM. Inlining is semantics-preserving for the VALUE and
        # >>> silently not for the CHECK, because the check was attached to the call node
        # >>> rather than to the callee.
        #
        # THE REPAIR PRESERVES THE CAPABILITY INSTEAD OF REFUSING: treat such a callee as
        # `#@ no_inline` FOR THIS CALLER ONLY, so the call survives to Module 6 and lands
        # on the existing, already-gated wrap. Nothing is rejected that used to be
        # accepted — the obligation simply becomes visible, which is what the user asked
        # for by writing `no_exception`. CENSUSED FIRST: across the 71 files declaring
        # `#@ no_exception`, NOT ONE also declares a module-global instance, so this is
        # byte-inert on the corpus today; it is a fence for the shape, not a migration.
        _ne = set((f.get("contracts") or {}).get("no_exception") or [])
        _ne_all = bool((f.get("contracts") or {}).get("no_exception_all", False))
        _keep_calls: Set[str] = set()
        if _ne or _ne_all:
            for _g in funcs:
                _draises = {r.get("exc_type")
                            for r in ((_g.get("contracts") or {}).get("raises") or [])}
                if _draises and (_ne_all or (_draises & _ne)):
                    _keep_calls.add(_g.get("name"))
        inliner.no_inline = (no_inline | _keep_calls) if _keep_calls else no_inline
        body = f.get("body", [])
        # (#33) EXPLICIT CONVERGENCE FLAG, not `for ... else`. The IR emitter reads only a
        # loop's body — `_process_for`/`_process_while` never look at `orelse` — so a loop
        # `else` was SILENTLY DROPPED from the model. `frontend/desugar.reject_loop_else`
        # now refuses the shape rather than dropping it; this is the mechanical rewrite it
        # asks for, and it is exactly semantics-preserving.
        _converged = False
        for _ in range(_MAX_INLINE_DEPTH):
            # (#49) ROUTE #169 — the caller's binders, recomputed per round (earlier rounds
            # add only freshened names).
            _cb = set(f.get("formal_params", []) or [])
            for _nd in _walk_dicts(body):
                if isinstance(_nd.get("target"), str) and _nd.get("stmt"):
                    _cb.add(_nd["target"])
                if isinstance(_nd.get("targets"), list) and _nd.get("stmt"):
                    _cb.update(t for t in _nd["targets"] if isinstance(t, str))
            inliner.caller_binders = _cb
            new_body = inliner.inline_stmts(body)
            if new_body == body:
                _converged = True
                break
            body = new_body
        if not _converged:
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

    # 11-1039-spec-10: an IMPORTED trusted stub (a `\trusted` cross-module wrapper,
    # e.g. `os.rmdir`) keeps its source body in the IR for provenance, but Module6
    # emits it body-less as a `val` defined by its contract alone — the body is
    # never verified or emitted. With the dependency's `module_globals` now
    # propagated (so `_filesystem.disk` types in the importer's contracts), that
    # dead wrapper body would otherwise be walked by the inliner, which tries to
    # inline its `_filesystem.sys_rmdir()` receivers against method records the
    # importer never imported — a spurious pipeline error on emission-dead code.
    # Exclude trusted stubs from the body-walking phases: their bodies are not part
    # of what is emitted/verified, so inlining/aliasing-checking them is a no-op.
    body_funcs = [f for f in funcs if not f.get("trusted")]

    # Phase 3: a module global is a single named object — forbid aliasing it (binding it
    # to a local or passing it as an argument), which would reintroduce the aliasing the
    # one-name model avoids. Checked on the ORIGINAL bodies (before inlining rewrites the
    # `g.m(args)` receivers away).
    _check_no_aliasing(body_funcs, globals_set)

    # Phase 2/3: inline method calls on globals (recursion-guarded, depth-bounded).
    # `funcs` (all) feeds the inliner's callee-lookup / recursion machinery;
    # `body_funcs` (non-trusted) are the only bodies actually rewritten.
    _inline_calls(funcs, globals_set, g_class, rewrite_funcs=body_funcs)

    # Phase 1: a function that (now) reads/writes a global field is not a pure logic
    # function — demote it so Module 6 emits a program `let` with the inferred effect.
    for f in funcs:
        if (_touches_global(f.get("body"), globals_set)
                or _touches_global(f.get("contracts"), globals_set)):
            f.pop("pure", None)
