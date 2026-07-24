"""bigger-build.md Phase 1 — the A-unit generic-fold recognizer + templater.

A *generic fold* (family A-unit, plan §1) is the type-derived catamorphism over
the compiler's ``Dict[str, Any]`` IR value: a self-recursive walk that descends a
``dict``/``list`` universal value and accumulates into a by-reference ``Set``/``dict``
parameter (``writes { acc }`` frame), the ``v2_iter_mutate_spike.mlw`` shape.

This module recognizes the closed, fail-closed pattern on the *IR* (the tuple
target ``k, v`` is erased to ``_for_target`` at ``Module5_IREmitter.py:1477``, but
the loop body still references the phantom key/value ``Var`` names and the
self-recursion, so the structure is fully recoverable) and emits, from the
matched node, the ``let rec walk … with walk_dict … with walk_list …`` group
mangled per method. The recursion comes from the ``pyval``/``pydict`` inductive
datatype (the ``needs_pydict`` L1 theory in ``preamble._emit_pydict_theory``), not
from the loop — so the ``size``-variant termination measure is a real structural
sub-term, closing the phase-2c defect (opaque ``iter_get`` had no sub-term).

The templater NEVER enters the TCB: a template bug yields an *unprovable*
instance (the ``--fun`` whole-body re-proof is loud), never a false proof, so the
3-axiom ledger is unchanged and no ``\trusted`` is weakened.

**Precision over recall.** A miss keeps the method ``\trusted`` (exactly as
today); a false fire would break byte-additivity, so every deviation from the
exact shape rejects. Verified inert (fires on 0/756 corpus programs → byte-diff
0); the poisoned control ``wall_v3_phase0/poison_ta.py`` is the single external
match that flips the gate red once.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

# The named irkey constructors the L1 preamble theory declares
# (`_emit_pydict_theory`). A literal schema key outside this set lowers to the
# `K_dyn "<key>"` computed-key fallback.
_NAMED_KEYS = {
    "type": "K_type", "left": "K_left", "right": "K_right", "op": "K_op",
    "z": "K_z", "value": "K_value", "target": "K_target", "body": "K_body",
    "orelse": "K_orelse", "func": "K_func", "name": "K_name",
}


def _irkey_ctor(key: str) -> str:
    """Map a literal schema key string to its irkey constructor term."""
    if key in _NAMED_KEYS:
        return _NAMED_KEYS[key]
    return f'(K_dyn "{key}")'


def _is_var(node: Any, name: Optional[str] = None) -> bool:
    if not isinstance(node, dict) or node.get("type") != "Var":
        return False
    return name is None or node.get("name") == name


def _is_string(node: Any) -> Optional[str]:
    if isinstance(node, dict) and node.get("type") == "String":
        return node.get("value")
    return None


def _match_isinstance(test: Any, subj: str, cls: str) -> bool:
    """`isinstance(<subj>, <cls>)` where cls is the bare name `dict`/`list`."""
    if not isinstance(test, dict) or test.get("type") != "Call":
        return False
    if test.get("func") != "isinstance":
        return False
    args = test.get("args", [])
    return (len(args) == 2 and _is_var(args[0], subj)
            and _is_var(args[1], cls))


def _match_pre_action(stmt: Any, subj: str, acc: str) -> Optional[Dict[str, str]]:
    """Optional pre-action:
        if obj.get("<gkey>") == "<gval>": targets.add(obj["<akey>"])
    Returns {guard_key, guard_val, add_key} or None if this stmt isn't it."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "If":
        return None
    if stmt.get("orelse"):
        return None
    test = stmt.get("test", {})
    if not isinstance(test, dict) or test.get("type") != "BinOp" or test.get("op") != "==":
        return None
    left, right = test.get("left", {}), test.get("right", {})
    # left = obj.get("<gkey>")
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == f"{subj}.get"):
        return None
    gargs = left.get("args", [])
    if len(gargs) != 1:
        return None
    gkey = _is_string(gargs[0])
    gval = _is_string(right)
    if gkey is None or gval is None:
        return None
    body = stmt.get("body", [])
    if len(body) != 1:
        return None
    add = body[0]
    if not (isinstance(add, dict) and add.get("stmt") == "Expr"):
        return None
    call = add.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add"):
        return None
    aargs = call.get("args", [])
    if len(aargs) != 1:
        return None
    sub = aargs[0]
    if not (isinstance(sub, dict) and sub.get("type") == "Subscript"
            and _is_var(sub.get("value"), subj)):
        return None
    akey = _is_string(sub.get("index"))
    if akey is None:
        return None
    return {"kind": "eq", "guard_key": gkey, "guard_val": gval, "add_key": akey}


def _match_pre_action_intuple(stmt: Any, subj: str,
                             acc: str) -> Optional[Dict[str, Any]]:
    """In-tuple + isinstance(str) pre-action (bigger-build A-unit grammar delta):

        if <subj>.get("<gkey>") in (<str-tuple>) and isinstance(<subj>.get("<akey>"), str):
            <acc>.add(<subj>["<akey>"])

    An `in`-tuple key-value guard over interned keys (constructor membership: is
    the `<gkey>` value one of the literal strings?) conjoined with an
    `isinstance(str)` narrowing of the *added* key `<akey>`, gating a
    `set_add` of `<subj>["<akey>"]`. Under the fixed `ensures True` contract the
    tuple/isinstance narrowings are pure boolean gates on WHICH string is added
    (they constrain neither type-safety nor termination), and the `isinstance
    str` maps EXACTLY to the `Some (PStr t)` reader arm — the faithful lowering
    reads `<akey>` and adds its string payload only when `<gkey>` matches a tuple
    element AND `<akey>` is a string. Returns
    {kind: "intuple_isinstance", guard_key, guard_vals, add_key} or None
    (fail-closed). The isinstance narrowing MUST target the same key as the add
    (a mismatch rejects), and every tuple element must be a string literal."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "If":
        return None
    if stmt.get("orelse"):
        return None
    test = stmt.get("test", {})
    if not (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "and"):
        return None
    left, right = test.get("left", {}), test.get("right", {})
    # left: <subj>.get("<gkey>") in (<str-tuple>)
    if not (isinstance(left, dict) and left.get("type") == "BinOp"
            and left.get("op") == "in"):
        return None
    lget = left.get("left", {})
    if not (isinstance(lget, dict) and lget.get("type") == "Call"
            and lget.get("func") == f"{subj}.get"
            and len(lget.get("args", [])) == 1):
        return None
    gkey = _is_string(lget["args"][0])
    if gkey is None:
        return None
    if not _is_string_tuple(left.get("right", {})):
        return None
    gvals = [_is_string(e) for e in left["right"]["elts"]]
    # right: isinstance(<subj>.get("<akey>"), str)
    if not (isinstance(right, dict) and right.get("type") == "Call"
            and right.get("func") == "isinstance"
            and len(right.get("args", [])) == 2):
        return None
    iarg, icls = right["args"][0], right["args"][1]
    if not (isinstance(iarg, dict) and iarg.get("type") == "Call"
            and iarg.get("func") == f"{subj}.get"
            and len(iarg.get("args", [])) == 1):
        return None
    akey_isi = _is_string(iarg["args"][0])
    if akey_isi is None or not _is_var(icls, "str"):
        return None
    # body: <acc>.add(<subj>["<akey>"])
    body = stmt.get("body", [])
    if len(body) != 1:
        return None
    add = body[0]
    if not (isinstance(add, dict) and add.get("stmt") == "Expr"):
        return None
    call = add.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add"
            and len(call.get("args", [])) == 1):
        return None
    sub = call["args"][0]
    if not (isinstance(sub, dict) and sub.get("type") == "Subscript"
            and _is_var(sub.get("value"), subj)):
        return None
    akey = _is_string(sub.get("index"))
    if akey is None or akey != akey_isi:
        return None
    return {"kind": "intuple_isinstance", "guard_key": gkey,
            "guard_vals": gvals, "add_key": akey}


def _flatten_and(node: Any) -> List[Any]:
    """Left-associatively flatten an `and`-tree into its conjunct list."""
    if (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "and"):
        return _flatten_and(node.get("left")) + _flatten_and(node.get("right"))
    return [node]


def _match_pre_action_nested_field(stmt: Any, subj: str,
                                   acc: str) -> Optional[Dict[str, Any]]:
    """Nested-field-read pre-action (bigger-build A-unit grammar delta):

        if <subj>.get("<gkey>") == "<gval>":
            <lv> = <subj>.get("<ckey>")
            if isinstance(<lv>, dict) and <lv>.get("<k1>") == "<v1>" and ... :
                <acc>.add(<lv>.get("<akey>"))

    An outer literal-key equality guard, a LOCAL bound to a *child* dict
    (`<subj>.get("<ckey>")`), then a nested guard that narrows the child to a
    dict (`isinstance(<lv>, dict)`) and constrains one-or-more of its literal
    keys, gating `set_add` of the child's `<akey>` value. Under the fixed
    `ensures True` contract the equality narrowings are pure boolean gates on
    WHICH string is added, and `isinstance(<lv>, dict)` maps EXACTLY to the
    `Some (PDict arr)` reader arm — the faithful lowering projects the child
    pydict and reads its literal keys. Returns
    {kind: "nested_field", guard_key, guard_val, child_key, field_guards, add_key}
    or None (fail-closed). The child-narrowing MUST be an `isinstance(<lv>, dict)`
    on the bound local, every field guard MUST be `<lv>.get(k)==v` on that same
    local, and the add MUST read a literal key of that local."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "If":
        return None
    if stmt.get("orelse"):
        return None
    outer = _match_eq_guard(stmt.get("test", {}), subj)
    if outer is None:
        return None
    gkey, gval = outer
    body = stmt.get("body", [])
    if len(body) != 2:
        return None
    # body[0]: <lv> = <subj>.get("<ckey>")
    asg = body[0]
    if not (isinstance(asg, dict) and asg.get("stmt") == "Assign"):
        return None
    lv = asg.get("target")
    if not isinstance(lv, str):
        return None
    cval = asg.get("value", {})
    if not (isinstance(cval, dict) and cval.get("type") == "Call"
            and cval.get("func") == f"{subj}.get"
            and len(cval.get("args", [])) == 1):
        return None
    ckey = _is_string(cval["args"][0])
    if ckey is None:
        return None
    # body[1]: if isinstance(<lv>,dict) and <lv>.get(k)==v and ... : <acc>.add(<lv>.get("<akey>"))
    inner = body[1]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If"):
        return None
    if inner.get("orelse"):
        return None
    conjuncts = _flatten_and(inner.get("test", {}))
    saw_isinstance = False
    field_guards: List[tuple] = []
    for c in conjuncts:
        if (isinstance(c, dict) and c.get("type") == "Call"
                and c.get("func") == "isinstance"
                and len(c.get("args", [])) == 2
                and _is_var(c["args"][0], lv) and _is_var(c["args"][1], "dict")):
            if saw_isinstance:
                return None
            saw_isinstance = True
            continue
        eq = _match_eq_guard(c, lv)
        if eq is None:
            return None
        field_guards.append(eq)
    if not saw_isinstance or not field_guards:
        return None
    ibody = inner.get("body", [])
    if len(ibody) != 1:
        return None
    add = ibody[0]
    if not (isinstance(add, dict) and add.get("stmt") == "Expr"):
        return None
    call = add.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add"
            and len(call.get("args", [])) == 1):
        return None
    av = call["args"][0]
    if not (isinstance(av, dict) and av.get("type") == "Call"
            and av.get("func") == f"{lv}.get"
            and len(av.get("args", [])) == 1):
        return None
    akey = _is_string(av["args"][0])
    if akey is None:
        return None
    return {"kind": "nested_field", "guard_key": gkey, "guard_val": gval,
            "child_key": ckey, "field_guards": field_guards, "add_key": akey}


def _match_dict_loop(stmt: Any, subj: str, acc: str, fname: str) -> Optional[Dict[str, Any]]:
    """`for k, v in obj.items(): [if k=="<skip>": continue]; f(v, targets)`
    or the `.values()` variant. Returns {skip_key: str|None} or None."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "For":
        return None
    it = stmt.get("iter", {})
    if not (isinstance(it, dict) and it.get("type") == "Call"
            and it.get("func") in (f"{subj}.items", f"{subj}.values")
            and not it.get("args")):
        return None
    body = list(stmt.get("body", []))
    skip_key: Optional[str] = None
    if body and isinstance(body[0], dict) and body[0].get("stmt") == "If":
        guard = body[0]
        if guard.get("orelse"):
            return None
        gt = guard.get("test", {})
        if not (isinstance(gt, dict) and gt.get("type") == "BinOp" and gt.get("op") == "=="):
            return None
        sk = _is_string(gt.get("right"))
        if sk is None or not _is_var(gt.get("left")):
            return None
        gbody = guard.get("body", [])
        if not (len(gbody) == 1 and isinstance(gbody[0], dict)
                and gbody[0].get("stmt") == "Continue"):
            return None
        skip_key = sk
        body = body[1:]
    # remaining body must be exactly the self-recursion `f(<value>, acc)`
    if len(body) != 1:
        return None
    rec = body[0]
    if not _match_self_recursion(rec, acc, fname):
        return None
    return {"skip_key": skip_key}


def _canon_call(cf: str) -> str:
    """Canonicalize a call-target string to the Module-5 emitted function name:
    a class-qualified static/self call `IRScanner.find_…` mangles to
    `irscanner__find_…` (lower(class) + `__` + method); a module-level call is
    already canonical."""
    if "." in cf:
        cls, meth = cf.rsplit(".", 1)
        return f"{cls.lower()}__{meth}"
    return cf


def _call_is_self(cf: Any, fname: str) -> bool:
    """True iff the call-target string names *this* function `fname` — the
    module-level bare name, the class-qualified static call (`Cls.meth` mangles
    to `cls__meth`), OR the instance self-recursion `self.<meth>` (the emitted
    name is `<class>__<meth>`, so `fname` ends with `__<meth>`). The `self.`
    form is fail-closed: a sibling call `self.other` has `meth == "other"` and
    `fname` (this method) does not end with `__other`, so it rejects."""
    if not isinstance(cf, str):
        return False
    if _canon_call(cf) == fname:
        return True
    if cf.startswith("self."):
        meth = cf[len("self."):]
        return bool(meth) and fname.endswith("__" + meth)
    return False


def _match_self_recursion(stmt: Any, acc: str, fname: str) -> bool:
    """`<self>(<value_var>, <acc>)` as an ExprStmt, where `<self>` resolves to
    this same function (module-level bare name, class-qualified static call, or
    instance-method `self.<meth>` self-recursion)."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Expr"):
        return False
    call = stmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return False
    if not _call_is_self(call.get("func"), fname):
        return False
    args = call.get("args", [])
    return (len(args) == 2 and _is_var(args[0]) and _is_var(args[1], acc))


def _match_list_loop(stmt: Any, subj: str, acc: str, fname: str) -> bool:
    """`for item in obj: f(item, targets)`."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "For":
        return False
    if not _is_var(stmt.get("iter"), subj):
        return False
    body = stmt.get("body", [])
    return len(body) == 1 and _match_self_recursion(body[0], acc, fname)


def recognize_generic_fold(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the A-unit generic-walk-and-mutate catamorphism.

    Returns a descriptor
        {subject, accumulator, pre_action|None, skip_key|None}
    when ``func``'s IR body is *exactly* the pattern; otherwise ``None`` (the
    method stays whatever it was — no fire). Never raises on a malformed node."""
    try:
        return _recognize(func)
    except Exception:
        return None


def _recognize(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 2:
        return None
    subj, acc = params[0], params[1]
    # The accumulator must be a set/dict parameter (by-ref collection).
    if func.get("param_annotations", {}).get(acc) not in ("set", "dict"):
        return None
    # The by-ref mutation must be DECLARED: the accumulator must appear in the
    # `#@ assigns` frame. A wrong / `\nothing` assigns on a mutating walk does NOT
    # fire (fail-closed) — closing the frame-fidelity gap where the templater's
    # `writes { acc }` would otherwise silently override (ignore) the contract's
    # declared frame. Keeps the emitted `writes { acc }` consistent with the
    # method's own `#@ assigns`.
    _assigns = func.get("contracts", {}).get("assigns", []) or []
    if not any(_is_var(a, acc) for a in _assigns):
        return None
    # A `-> None` unit fold (result algebra = UNIT).
    if func.get("return_annotation") not in ("None", None):
        return None
    fname = func["name"]

    body = func.get("body", [])
    if len(body) != 1:
        return None
    outer = body[0]
    if not (isinstance(outer, dict) and outer.get("stmt") == "If"):
        return None
    if not _match_isinstance(outer.get("test", {}), subj, "dict"):
        return None

    # dict-arm body: optional pre-action then the dict loop.
    dbody = list(outer.get("body", []))
    pre = None
    if dbody:
        maybe_pre = _match_pre_action(dbody[0], subj, acc)
        if maybe_pre is None:
            maybe_pre = _match_pre_action_intuple(dbody[0], subj, acc)
        if maybe_pre is None:
            maybe_pre = _match_pre_action_nested_field(dbody[0], subj, acc)
        if maybe_pre is not None:
            pre = maybe_pre
            dbody = dbody[1:]
    if len(dbody) != 1:
        return None
    dloop = _match_dict_loop(dbody[0], subj, acc, fname)
    if dloop_is_none(dloop):
        return None

    # else-arm: exactly `if isinstance(obj, list): for item in obj: f(item, acc)`
    orelse = outer.get("orelse", [])
    if len(orelse) != 1:
        return None
    inner = orelse[0]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If"):
        return None
    if inner.get("orelse"):
        return None
    if not _match_isinstance(inner.get("test", {}), subj, "list"):
        return None
    ibody = inner.get("body", [])
    if len(ibody) != 1 or not _match_list_loop(ibody[0], subj, acc, fname):
        return None

    return {
        "subject": subj,
        "accumulator": acc,
        "pre_action": pre,
        "skip_key": dloop["skip_key"],
    }


def dloop_is_none(dloop: Any) -> bool:
    return dloop is None


def emit_generic_fold_group(func: Dict[str, Any], gf: Dict[str, Any],
                            whyml_ident) -> List[str]:
    """Emit the type-derived catamorphism group for a recognized A-unit fold.

    The text is the compile-time defunctionalization of the walk (no HOF reaches
    a VC): specialized literal-key readers (constructor match, zero string
    theory), an inlined pre-action, and the ``let rec walk … with walk_dict …
    with walk_list …`` group over the ``pyval``/``pydict`` datatype, mangled per
    method. Reuses the L1 preamble theory (``size``/``size_dict``/``size_list`` +
    the proven lemma pack) for the ``variant`` decrease. Congruent (modulo
    holes/names) to the proven ``v2_iter_mutate_spike.mlw``."""
    n = whyml_ident(func["name"])
    subj = gf["subject"]
    acc = gf["accumulator"]
    acc_ty = "ref (map string bool)"
    out: List[str] = []

    pre = gf["pre_action"]
    # ---- literal-key readers (only those the pre-action needs) ----
    reader_names: Dict[str, str] = {}
    _emitted_readers: set = set()

    def _emit_reader(key: str) -> str:
        """Emit (once) a literal-key spine reader for `key`; return its name.
        A single generic `pydict -> option pyval` reader works on ANY pydict
        (the walked node OR a projected child), so it is shared by key."""
        rname = f"{n}__get_{_reader_suffix(key)}"
        reader_names[key] = rname
        if rname in _emitted_readers:
            return rname
        _emitted_readers.add(rname)
        out.append(f"  let rec {rname} (d: pydict) : option pyval")
        out.append("    variant { d }")
        out.append("  = match d with")
        out.append("    | DNil -> None")
        if key in _NAMED_KEYS:
            # interned constructor — direct pattern match, zero string theory.
            out.append(f"    | DCons {_NAMED_KEYS[key]} v _ -> Some v")
            out.append(f"    | DCons _ _ rest -> {rname} rest")
        else:
            # computed key `K_dyn s` — a string literal cannot appear in a
            # pattern, so match the `K_dyn s` cell and test the payload.
            out.append(f'    | DCons (K_dyn s) v rest -> if pystr_eq s "{key}" then Some v else {rname} rest')
            out.append(f"    | DCons _ _ rest -> {rname} rest")
        out.append("    end")
        return rname

    if pre is not None:
        if pre.get("kind") == "nested_field":
            needed = ([pre["guard_key"], pre["child_key"]]
                      + [k for k, _ in pre["field_guards"]] + [pre["add_key"]])
        else:
            needed = [pre["guard_key"], pre["add_key"]]
        for key in needed:
            _emit_reader(key)

    # ---- inlined pre-action ----
    if pre is not None and pre.get("kind") == "nested_field":
        gname = reader_names[pre["guard_key"]]
        cname = reader_names[pre["child_key"]]
        aname = reader_names[pre["add_key"]]
        out.append(f"  let {n}__pre (d: pydict) ({acc}: {acc_ty}) : unit")
        out.append(f"    writes {{ {acc} }}")
        out.append(f"  = match {gname} d with")
        out.append("    | Some (PStr s) ->")
        out.append(f'        if pystr_eq s "{pre["guard_val"]}" then')
        # project the child pydict (`isinstance(<lv>, dict)` -> `Some (PDict arr)`)
        out.append(f"          (match {cname} d with")
        out.append("           | Some (PDict arr) ->")
        # nest one literal-key equality gate per field guard, innermost = the add.
        indent = "               "
        closers: List[str] = []
        for (fk, fv) in pre["field_guards"]:
            fname_r = reader_names[fk]
            out.append(f"{indent}(match {fname_r} arr with")
            out.append(f"{indent} | Some (PStr c) -> if pystr_eq c \"{fv}\" then")
            closers.append(f"{indent}   else () | _ -> () end)")
            indent += "   "
        out.append(f"{indent}(match {aname} arr with")
        out.append(f"{indent} | Some (PStr f) -> {acc} := set_add !{acc} f")
        out.append(f"{indent} | _ -> () end)")
        for cl in reversed(closers):
            out.append(cl)
        out.append("           | _ -> () end)")
        out.append("        else ()")
        out.append("    | _ -> () end")
    elif pre is not None:
        gname = reader_names[pre["guard_key"]]
        aname = reader_names[pre["add_key"]]
        if pre.get("kind") == "intuple_isinstance":
            # disjunction over the tuple's string elements — parenthesized so the
            # `||` chain binds inside the `if` test.
            cond = "(" + " || ".join(f'pystr_eq s "{v}"' for v in pre["guard_vals"]) + ")"
        else:
            # single-value equality — emitted UNPARENTHESIZED to stay byte-identical
            # to the pre-extension A-unit output (strict additivity).
            cond = f'pystr_eq s "{pre["guard_val"]}"'
        out.append(f"  let {n}__pre (d: pydict) ({acc}: {acc_ty}) : unit")
        out.append(f"    writes {{ {acc} }}")
        out.append(f"  = match {gname} d with")
        out.append("    | Some (PStr s) ->")
        out.append(f"        if {cond} then")
        out.append(f"          (match {aname} d with")
        out.append(f"           | Some (PStr t) -> {acc} := set_add !{acc} t")
        out.append("           | _ -> () end)")
        out.append("        else ()")
        out.append("    | _ -> () end")

    # ---- skip-key predicate (if the dict loop has a literal-key skip guard) ----
    skip = gf["skip_key"]
    if skip is not None:
        out.append(f"  let {n}__skip (k: irkey) : bool")
        if skip in _NAMED_KEYS:
            out.append(f"  = match k with {_NAMED_KEYS[skip]} -> true | _ -> false end")
        else:
            out.append(f'  = match k with K_dyn s -> pystr_eq s "{skip}" | _ -> false end')

    # ---- the walk / walk_dict / walk_list catamorphism group ----
    pre_call = f"{n}__pre d {acc}; " if pre is not None else ""
    out.append(f"  let rec {n} ({subj}: pyval) ({acc}: {acc_ty}) : unit")
    out.append("    requires { true } ensures { true }")
    out.append(f"    writes {{ {acc} }} variant {{ pv_size {subj} }}")
    out.append(f"  = match {subj} with")
    out.append(f"    | PDict d -> {pre_call}{n}__dict d {acc}")
    out.append(f"    | PList xs -> {n}__list xs {acc}")
    out.append("    | _ -> () end")
    out.append(f"  with {n}__dict (d: pydict) ({acc}: {acc_ty}) : unit")
    out.append("    requires { true } ensures { true }")
    out.append(f"    writes {{ {acc} }} variant {{ size_dict d }}")
    out.append("  = match d with")
    out.append("    | DNil -> ()")
    if skip is not None:
        out.append("    | DCons k v rest ->")
        out.append(f"        (if {n}__skip k then () else {n} v {acc});")
        out.append(f"        {n}__dict rest {acc}")
    else:
        out.append(f"    | DCons _ v rest -> {n} v {acc}; {n}__dict rest {acc}")
    out.append("    end")
    out.append(f"  with {n}__list (xs: list pyval) ({acc}: {acc_ty}) : unit")
    out.append("    requires { true } ensures { true }")
    out.append(f"    writes {{ {acc} }} variant {{ size_list xs }}")
    out.append(f"  = match xs with Nil -> () | Cons h t -> {n} h {acc}; {n}__list t {acc} end")
    return out


def _reader_suffix(key: str) -> str:
    """A WhyML-safe reader name suffix for a literal key."""
    if key in _NAMED_KEYS:
        return _NAMED_KEYS[key]
    return "dyn_" + "".join(c if c.isalnum() else "_" for c in key)


# =========================================================================
# phase3.md §3.1 — A-SET returned-set fold (result_algebra = SET, by return).
#
# The by-RETURN twin of the A-unit by-ref catamorphism. Instead of mutating a
# `targets: ref (map string bool)` accumulator parameter under a `writes` frame,
# the A-set fold builds a fresh local `set()`, unions the recursive results into
# it (`acc |= self(v)`), and RETURNS it. The WhyML lowering is FUNCTIONAL
# (`assigns \nothing`; no `writes` clause): `walk`/`walk_dict`/`walk_list` each
# return `map string bool` (the certified L1 set repr), combined by `set_union`
# (pointwise or, purely DEFINED in the preamble — no axiom). Proven whole-body in
# `v2_setfold_spike.mlw` on Alt-Ergo AND Z3.
#
# Fail-closed exactly as A-unit: a miss keeps the method `\trusted`; a template
# bug yields an unprovable instance (the full-file re-proof is loud), never a
# false proof. Threaded read-only `set` parameters (e.g. `func_names_set`) are
# passed unchanged through every recursive call and modelled `map string bool`.
# =========================================================================


def _match_eq_guard(node: Any, subj: str) -> Optional[tuple]:
    """`<subj>.get("<gkey>") == "<gval>"` → (gkey, gval) or None."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "=="):
        return None
    left, right = node.get("left", {}), node.get("right", {})
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == f"{subj}.get"):
        return None
    gargs = left.get("args", [])
    if len(gargs) != 1:
        return None
    gkey = _is_string(gargs[0])
    gval = _is_string(right)
    if gkey is None or gval is None:
        return None
    return (gkey, gval)


def _match_in_guard(node: Any, subj: str, extra: List[str]) -> Optional[tuple]:
    """`<subj>.get("<mkey>") in <extra_set_param>` → (mkey, param) or None.
    The right operand must be one of the threaded `set`-typed parameters."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "in"):
        return None
    left, right = node.get("left", {}), node.get("right", {})
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == f"{subj}.get"):
        return None
    margs = left.get("args", [])
    if len(margs) != 1:
        return None
    mkey = _is_string(margs[0])
    if mkey is None:
        return None
    if not (_is_var(right) and right.get("name") in extra):
        return None
    return (mkey, right.get("name"))


def _match_set_guard(test: Any, subj: str, extra: List[str]) -> Optional[Dict[str, Any]]:
    """The pre-action guard: either the simple `.get(k)==v`, or the compound
    `.get(k)==v and .get(mk) in <set param>`. Returns a descriptor or None."""
    simple = _match_eq_guard(test, subj)
    if simple is not None:
        return {"kind": "eq", "guard_key": simple[0], "guard_val": simple[1],
                "mem_key": None, "mem_param": None}
    if (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "and"):
        left = _match_eq_guard(test.get("left", {}), subj)
        mem = _match_in_guard(test.get("right", {}), subj, extra)
        if left is not None and mem is not None:
            return {"kind": "eq", "guard_key": left[0], "guard_val": left[1],
                    "mem_key": mem[0], "mem_param": mem[1]}
    return None


def _is_string_tuple(node: Any) -> bool:
    """A literal tuple all of whose elements are string literals."""
    if not (isinstance(node, dict) and node.get("type") == "Tuple"):
        return False
    elts = node.get("elts", [])
    return bool(elts) and all(_is_string(e) is not None for e in elts)


def _match_set_pre_action_tuple(stmt: Any, subj: str,
                                acc: str) -> Optional[Dict[str, Any]]:
    """Second pre-action shape (the `collection_binder_kinds` form):

        if <subj>.get("<gkey>") in (<str-tuple>):
            <lv> = <subj>.get("<akey>")
            if <lv> in (<str-tuple>):
                <acc>.add(<lv>)

    An outer `in`-tuple type guard, a local bound from a literal-key `.get`, a
    nested `in`-tuple narrowing guard, and `acc.add(<local>)`. Under the fixed
    `ensures True` contract the tuple narrowings are pure boolean gates on the
    added STRING (they constrain WHICH strings, not the type/termination), so the
    faithful lowering reads `<akey>` and adds its string payload. Returns
    {kind: "local_read", add_key} or None (fail-closed)."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "If":
        return None
    if stmt.get("orelse"):
        return None
    test = stmt.get("test", {})
    # outer guard: <subj>.get("<gkey>") in (<str-tuple>)
    if not (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "in"):
        return None
    left = test.get("left", {})
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == f"{subj}.get"
            and len(left.get("args", [])) == 1
            and _is_string(left["args"][0]) is not None):
        return None
    if not _is_string_tuple(test.get("right", {})):
        return None
    body = stmt.get("body", [])
    if len(body) != 2:
        return None
    # body[0]: <lv> = <subj>.get("<akey>")
    asg = body[0]
    if not (isinstance(asg, dict) and asg.get("stmt") == "Assign"):
        return None
    lv = asg.get("target")
    if not isinstance(lv, str):
        return None
    aval = asg.get("value", {})
    if not (isinstance(aval, dict) and aval.get("type") == "Call"
            and aval.get("func") == f"{subj}.get"
            and len(aval.get("args", [])) == 1):
        return None
    akey = _is_string(aval["args"][0])
    if akey is None:
        return None
    # body[1]: if <lv> in (<str-tuple>): <acc>.add(<lv>)
    inner = body[1]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If"):
        return None
    if inner.get("orelse"):
        return None
    itest = inner.get("test", {})
    if not (isinstance(itest, dict) and itest.get("type") == "BinOp"
            and itest.get("op") == "in" and _is_var(itest.get("left"), lv)
            and _is_string_tuple(itest.get("right", {}))):
        return None
    ibody = inner.get("body", [])
    if len(ibody) != 1:
        return None
    add = ibody[0]
    if not (isinstance(add, dict) and add.get("stmt") == "Expr"):
        return None
    call = add.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add"
            and len(call.get("args", [])) == 1
            and _is_var(call["args"][0], lv)):
        return None
    return {"kind": "local_read", "add_key": akey}


def _match_set_pre_action(stmt: Any, subj: str, acc: str,
                          extra: List[str]) -> Optional[Dict[str, Any]]:
    """Optional pre-action: `if <guard>: <acc>.add(<subj>["<akey>"])`.
    Returns {guard_key, guard_val, mem_key|None, mem_param|None, add_key}."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "If":
        return None
    if stmt.get("orelse"):
        return None
    guard = _match_set_guard(stmt.get("test", {}), subj, extra)
    if guard is None:
        return None
    body = stmt.get("body", [])
    if len(body) != 1:
        return None
    add = body[0]
    if not (isinstance(add, dict) and add.get("stmt") == "Expr"):
        return None
    call = add.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add"):
        return None
    aargs = call.get("args", [])
    if len(aargs) != 1:
        return None
    sub = aargs[0]
    if not (isinstance(sub, dict) and sub.get("type") == "Subscript"
            and _is_var(sub.get("value"), subj)):
        return None
    akey = _is_string(sub.get("index"))
    if akey is None:
        return None
    guard["add_key"] = akey
    return guard


def _match_set_union_rec(stmt: Any, acc: str, fname: str, extra: List[str]) -> bool:
    """`<acc> |= <self>(<loopvar>, <extra...>)` — the union accumulation.
    An AugAssign with op `|`, target the returned-set local, value a self-call
    whose first arg is the loop var and whose remaining args are the threaded
    parameters in order."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "AugAssign"):
        return False
    if stmt.get("target") != acc or stmt.get("op") != "|":
        return False
    call = stmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return False
    cf = call.get("func")
    if not isinstance(cf, str) or _canon_call(cf) != fname:
        return False
    args = call.get("args", [])
    if len(args) != 1 + len(extra):
        return False
    if not _is_var(args[0]):
        return False
    return all(_is_var(args[1 + i], e) for i, e in enumerate(extra))


def _match_set_dict_loop(stmt: Any, subj: str, acc: str, fname: str,
                         extra: List[str]) -> Optional[Dict[str, Any]]:
    """`for k,v in obj.items()/.values(): [if k=="<skip>": continue]; acc |= self(v,…)`."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "For":
        return None
    it = stmt.get("iter", {})
    if not (isinstance(it, dict) and it.get("type") == "Call"
            and it.get("func") in (f"{subj}.items", f"{subj}.values")
            and not it.get("args")):
        return None
    body = list(stmt.get("body", []))
    skip_key: Optional[str] = None
    if body and isinstance(body[0], dict) and body[0].get("stmt") == "If":
        guard = body[0]
        if guard.get("orelse"):
            return None
        gt = guard.get("test", {})
        if not (isinstance(gt, dict) and gt.get("type") == "BinOp" and gt.get("op") == "=="):
            return None
        sk = _is_string(gt.get("right"))
        if sk is None or not _is_var(gt.get("left")):
            return None
        gbody = guard.get("body", [])
        if not (len(gbody) == 1 and isinstance(gbody[0], dict)
                and gbody[0].get("stmt") == "Continue"):
            return None
        skip_key = sk
        body = body[1:]
    if len(body) != 1 or not _match_set_union_rec(body[0], acc, fname, extra):
        return None
    return {"skip_key": skip_key}


def _match_set_list_loop(stmt: Any, subj: str, acc: str, fname: str,
                         extra: List[str]) -> bool:
    """`for item in obj: acc |= self(item, …)`."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "For":
        return False
    if not _is_var(stmt.get("iter"), subj):
        return False
    body = stmt.get("body", [])
    return len(body) == 1 and _match_set_union_rec(body[0], acc, fname, extra)


def recognize_setfold(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the A-set returned-set generic fold (phase3.md §3.1).

    Returns {subject, acc_local, extra_params, pre_action|None, skip_key|None}
    when the IR body is *exactly* the returned-set catamorphism; else None."""
    try:
        return _recognize_setfold(func)
    except Exception:
        return None


def _recognize_setfold(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if not params:
        return None
    subj = params[0]
    extra = params[1:]
    pa = func.get("param_annotations", {})
    # Every threaded parameter must be a read-only `set` (Set[str] → map string
    # bool). A non-set extra param (str/int/dict) rejects — fail-closed.
    for e in extra:
        if pa.get(e) != "set":
            return None
    # The result algebra is a returned set.
    if func.get("return_annotation") != "set":
        return None
    fname = func["name"]

    body = func.get("body", [])
    if len(body) != 3:
        return None
    init, outer, ret = body

    # init: `<acc> = set()`
    if not (isinstance(init, dict) and init.get("stmt") == "Assign"):
        return None
    acc = init.get("target")
    if not isinstance(acc, str):
        return None
    iv = init.get("value")
    if not (isinstance(iv, dict) and iv.get("type") == "Call"
            and iv.get("func") == "set" and not iv.get("args")):
        return None
    # The returned-set local must be distinct from the walked subject (a fold,
    # not an in-place rewrite of the subject).
    if acc == subj:
        return None

    # ret: `return <acc>`
    if not (isinstance(ret, dict) and ret.get("stmt") == "Return"
            and _is_var(ret.get("value"), acc)):
        return None

    # outer: `if isinstance(<subj>, dict): …`
    if not (isinstance(outer, dict) and outer.get("stmt") == "If"):
        return None
    if not _match_isinstance(outer.get("test", {}), subj, "dict"):
        return None

    dbody = list(outer.get("body", []))
    pre = None
    if dbody:
        maybe = _match_set_pre_action(dbody[0], subj, acc, extra)
        if maybe is None:
            maybe = _match_set_pre_action_tuple(dbody[0], subj, acc)
        if maybe is not None:
            pre = maybe
            dbody = dbody[1:]
    if len(dbody) != 1:
        return None
    dloop = _match_set_dict_loop(dbody[0], subj, acc, fname, extra)
    if dloop is None:
        return None

    orelse = outer.get("orelse", [])
    if len(orelse) != 1:
        return None
    inner = orelse[0]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If"):
        return None
    if inner.get("orelse"):
        return None
    if not _match_isinstance(inner.get("test", {}), subj, "list"):
        return None
    ibody = inner.get("body", [])
    if len(ibody) != 1 or not _match_set_list_loop(ibody[0], subj, acc, fname, extra):
        return None

    return {
        "subject": subj,
        "acc_local": acc,
        "extra_params": extra,
        "pre_action": pre,
        "skip_key": dloop["skip_key"],
    }


def _setfold_leaf_empty_lines() -> List[str]:
    """richer-contracts-bridge P2.2 (C2): the RELATIONAL `setfold_leaf_empty`
    predicate — a set fold's output on a NON-container (leaf) input is the EMPTY
    set (the set-fold analog of decoder totality / `None => skipped`). Pure
    definition, NO axiom; the fact discharges from the top function's leaf arm
    (`_ -> const false`) alone."""
    return [
        "  (* richer-contracts-bridge P2.2 (C2): a set fold maps a leaf (non-dict,",
        "     non-list) input to the EMPTY set — its output domain is drawn only",
        "     from container structure. Pure definition, NO axiom. *)",
        "  predicate setfold_leaf_empty (v: pyval) (r: map string bool)",
        "  = match v with",
        "    | PDict _ -> true",
        "    | PList _ -> true",
        "    | _ -> r = (const false : map string bool)",
        "    end",
    ]


def emit_setfold_group(func: Dict[str, Any], sf: Dict[str, Any],
                       whyml_ident, top_ensures: Optional[List[str]] = None) -> List[str]:
    """Emit the returned-set catamorphism group for a recognized A-set fold.

    Functional (`assigns \\nothing`; no `writes` frame): every function returns
    `map string bool`, combined by the preamble's purely-defined `set_union`.
    Threaded read-only `set` parameters are typed `map string bool` and passed
    through. Congruent (modulo names) to the proven `v2_setfold_spike.mlw`.

    richer-contracts-bridge P2.2: the TOP-level function carries the METHOD's own
    `#@ ensures` (`top_ensures`, default `["true"]` => byte-identical historical
    `ensures { true }`). A relational `setfold_leaf_empty(subj, \\result)` fact is
    emitted alongside its predicate; helpers keep `ensures { true }`."""
    n = whyml_ident(func["name"])
    subj = sf["subject"]
    extra = sf["extra_params"]
    pre = sf["pre_action"]
    skip = sf["skip_key"]

    extra_sig = "".join(f" ({whyml_ident(e)}: map string bool)" for e in extra)
    extra_args = "".join(f" {whyml_ident(e)}" for e in extra)
    out: List[str] = []
    _te = list(top_ensures or ["true"])
    if any("setfold_leaf_empty" in c for c in _te):
        out.extend(_setfold_leaf_empty_lines())

    # ---- literal-key readers (guard / membership / add keys the pre needs) ----
    if pre is not None:
        if pre["kind"] == "local_read":
            keys = [pre["add_key"]]
        else:
            keys = [pre["guard_key"], pre.get("mem_key"), pre["add_key"]]
        seen: Dict[str, str] = {}
        for key in keys:
            if key is None or key in seen:
                continue
            rname = f"{n}__get_{_reader_suffix(key)}"
            seen[key] = rname
            out.append(f"  let rec {rname} (d: pydict) : option pyval")
            out.append("    variant { d }")
            out.append("  = match d with")
            out.append("    | DNil -> None")
            if key in _NAMED_KEYS:
                # interned constructor — direct pattern match, zero string theory.
                out.append(f"    | DCons {_NAMED_KEYS[key]} v _ -> Some v")
                out.append(f"    | DCons _ _ rest -> {rname} rest")
            else:
                # computed key `K_dyn s` — a string literal cannot appear in a
                # pattern, so match the `K_dyn s` cell and test the payload.
                out.append(f'    | DCons (K_dyn s) v rest -> if pystr_eq s "{key}" then Some v else {rname} rest')
                out.append(f"    | DCons _ _ rest -> {rname} rest")
            out.append("    end")

        aname = f"{n}__get_{_reader_suffix(pre['add_key'])}"
        out.append(f"  let {n}__pre (d: pydict){extra_sig} : map string bool")
        if pre["kind"] == "local_read":
            # The `.get(<akey>)` read, added when a string is present (the tuple
            # narrowings are boolean-only under the `ensures True` contract).
            out.append(f"  = match {aname} d with")
            out.append("    | Some (PStr t) -> set_add (const false) t")
            out.append("    | _ -> const false end")
        else:
            gname = f"{n}__get_{_reader_suffix(pre['guard_key'])}"
            out.append(f"  = match {gname} d with")
            out.append("    | Some (PStr s) ->")
            out.append(f'        if pystr_eq s "{pre["guard_val"]}" then')
            if pre.get("mem_key") is not None:
                mname = f"{n}__get_{_reader_suffix(pre['mem_key'])}"
                mparam = whyml_ident(pre["mem_param"])
                out.append(f"          (match {mname} d with")
                out.append("           | Some (PStr m) ->")
                out.append(f"               if Map.get {mparam} m then")
                out.append(f"                 (match {aname} d with")
                out.append("                  | Some (PStr t) -> set_add (const false) t")
                out.append("                  | _ -> const false end)")
                out.append("               else const false")
                out.append("           | _ -> const false end)")
            else:
                out.append(f"          (match {aname} d with")
                out.append("           | Some (PStr t) -> set_add (const false) t")
                out.append("           | _ -> const false end)")
            out.append("        else const false")
            out.append("    | _ -> const false end")

    # ---- skip-key predicate (literal-key skip in the dict loop) ----
    if skip is not None:
        out.append(f"  let {n}__skip (k: irkey) : bool")
        if skip in _NAMED_KEYS:
            out.append(f"  = match k with {_NAMED_KEYS[skip]} -> true | _ -> false end")
        else:
            out.append(f'  = match k with K_dyn s -> pystr_eq s "{skip}" | _ -> false end')

    # ---- the walk / walk_dict / walk_list returned-set group ----
    pre_term = (f"set_union ({n}__pre d{extra_args}) ({n}__dict d{extra_args})"
                if pre is not None else f"{n}__dict d{extra_args}")
    _ens_line = "".join(f" ensures {{ {e} }}" for e in _te)
    out.append(f"  let rec {n} ({subj}: pyval){extra_sig} : map string bool")
    out.append(f"    requires {{ true }}{_ens_line}")
    out.append(f"    variant {{ pv_size {subj} }}")
    out.append(f"  = match {subj} with")
    out.append(f"    | PDict d -> {pre_term}")
    out.append(f"    | PList xs -> {n}__list xs{extra_args}")
    out.append("    | _ -> const false end")
    out.append(f"  with {n}__dict (d: pydict){extra_sig} : map string bool")
    out.append("    requires { true } ensures { true }")
    out.append("    variant { size_dict d }")
    out.append("  = match d with")
    out.append("    | DNil -> const false")
    if skip is not None:
        out.append("    | DCons k v rest ->")
        out.append(f"        set_union (if {n}__skip k then const false else {n} v{extra_args})")
        out.append(f"                  ({n}__dict rest{extra_args})")
    else:
        out.append(f"    | DCons _ v rest -> set_union ({n} v{extra_args}) ({n}__dict rest{extra_args})")
    out.append("    end")
    out.append(f"  with {n}__list (xs: list pyval){extra_sig} : map string bool")
    out.append("    requires { true } ensures { true }")
    out.append("    variant { size_list xs }")
    out.append(f"  = match xs with Nil -> const false")
    out.append(f"    | Cons h t -> set_union ({n} h{extra_args}) ({n}__list t{extra_args}) end")
    return out


# =========================================================================
# ir-traversal-residual T1 — the FUNCTORIAL-MAP (reconstruction) algebra
# (result_algebra = the value type itself), plus insight C (guard classif.).
#
# The reconstruction twin of the read-only folds: instead of accumulating into
# a fixed algebra, the walk BUILDS a fresh `pyval`/`pydict`/`list pyval`,
# rewriting selected `DCons` cells and rebuilding the rest structurally. The
# stated obstacles dissolve under the project scope cut:
#
#   * TERMINATION — the `variant` decreases on the INPUT (`size node`), exactly
#     as in the read-only folds; building `DCons` cells on the way up is
#     constructor application (total by definition).
#   * FRAME — the WhyML emission is purely functional (returns a fresh value),
#     so `assigns \nothing` is trivial (no `writes`).
#   * VALUE-DEPENDENT BRANCHING (insight C) — a rewrite guard `v == tvar`
#     compares the walked value to a runtime STRING parameter. It is a SEMANTIC
#     guard: compiled to the concretely-defined `pystr_eq` boolean whose result
#     NO VC constrains (both arms are type-safe independently). The KEY test
#     (`k == "name"`) is a STRUCTURAL DISCRIMINANT (interned-`irkey` constructor
#     match, zero string theory). The replacement value `PStr concrete` is
#     well-typed by construction. No projection's type-safety is dominated by a
#     semantic guard (the replacement is a `str` param and the recursion returns
#     a `pyval` in BOTH arms), so the guard-dominance check (plan §1/§7) passes
#     and the method is cleanly convertible.
#
# NO wf-preservation certificate is needed: `pyval` carries no well-formedness
# TYPE invariant (`wf_ir` is a separate PREDICATE the group never references
# under `ensures True`), and every rebuilt key is copied verbatim from the input
# (`DCons k … `), so type-safety needs no key-shape lemma. Ledger stays at 3.
#
# SCOPE-CUT NOTE (honest, type-safety-only): the emitted model faithfully
# encodes reconstruction + the key discriminant + the opaque `v==tvar` guard +
# the `PStr concrete` replacement. Two SOURCE guards that only NARROW *which*
# cells are rewritten are value-refinements the `ensures True` contract makes
# irrelevant and are deliberately not re-modelled: (a) the extra
# `node.get("type")=="Var"` conjunct on the name-rewrite; (b) the post-loop
# `new["type"]==tvar` rewrite is folded into the same per-cell rule for the
# `type` key (identical type behaviour). Both make the model rewrite in a
# SUPERSET of the source's cases — sound under type-safety-only (Q6 scope cut).
#
# Fail-closed exactly as the folds: a miss keeps the method `\trusted`; a
# template bug yields an unprovable instance (the full-file re-proof is loud),
# never a false proof. Verified inert on the reference corpus (byte-diff 0); a
# poisoned control is the single external match that flips the gate red once.
# =========================================================================


def _is_dictlit_empty(node: Any) -> bool:
    """`{}` — an empty dict literal (the fresh accumulator `new = {}`)."""
    return (isinstance(node, dict) and node.get("type") == "DictLit"
            and not node.get("keys") and not node.get("values"))


def _match_substmap_guard(test: Any, tvar_p: str) -> Optional[tuple]:
    """A rewrite guard: a conjunction that MUST contain a key-literal test
    `<keyvar> == "<lit>"` and a value test `<valvar> == <tvar_p>` (either
    operand order). Extra conjuncts (e.g. `node.get("type")=="Var"`) are
    permitted and IGNORED — they only narrow *which* cells rewrite (a value
    fact the `ensures True` contract does not need). Returns
    (lit_key, keyvar, valvar) or None (fail-closed if either mandatory conjunct
    is absent)."""
    lit_key: Optional[str] = None
    keyvar: Optional[str] = None
    valvar: Optional[str] = None
    for c in _flatten_and(test):
        if not (isinstance(c, dict) and c.get("type") == "BinOp"
                and c.get("op") == "=="):
            continue
        l, r = c.get("left", {}), c.get("right", {})
        # <keyvar> == "<lit>"
        if _is_var(l) and _is_string(r) is not None and lit_key is None:
            keyvar = l.get("name")
            lit_key = _is_string(r)
            continue
        # <valvar> == <tvar_p>  (either order)
        if _is_var(l) and _is_var(r):
            if r.get("name") == tvar_p and valvar is None:
                valvar = l.get("name")
            elif l.get("name") == tvar_p and valvar is None:
                valvar = r.get("name")
    if lit_key is None or keyvar is None or valvar is None:
        return None
    return (lit_key, keyvar, valvar)


def _match_arrayset(stmt: Any, arrvar: str, idxvar: str) -> Optional[Any]:
    """`<arrvar>[<idxvar>] = <value>` (ArraySet). Returns the RHS value node
    or None. `idxvar` is the loop key Var; the index MUST be `Var(idxvar)`."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "ArraySet"):
        return None
    if not _is_var(stmt.get("array"), arrvar):
        return None
    if not _is_var(stmt.get("index"), idxvar):
        return None
    return stmt.get("value")


def _is_self_rec_call(node: Any, valvar: str, tvar_p: str,
                      concrete_p: str, fname: str) -> bool:
    """`<self>(<valvar>, <tvar_p>, <concrete_p>)` — the reconstruction
    self-recursion on the cell value."""
    if not (isinstance(node, dict) and node.get("type") == "Call"):
        return False
    if not _call_is_self(node.get("func"), fname):
        return False
    args = node.get("args", [])
    return (len(args) == 3 and _is_var(args[0], valvar)
            and _is_var(args[1], tvar_p) and _is_var(args[2], concrete_p))


def _chain_rec(node: Any, newvar: str, tvar_p: str, concrete_p: str,
               fname: str) -> Optional[tuple]:
    """Parse the per-item `if/elif …: new[k]=concrete else: new[k]=self(v,…)`
    rewrite chain. Returns (rewrite_keys, keyvar, valvar) or None. Each `if`
    arm rewrites the SAME key var to `concrete`; the terminal `else` rebuilds
    via the self-recursion."""
    if not (isinstance(node, dict) and node.get("stmt") == "If"):
        return None
    g = _match_substmap_guard(node.get("test", {}), tvar_p)
    if g is None:
        return None
    lit_key, keyvar, valvar = g
    nbody = node.get("body", [])
    if len(nbody) != 1:
        return None
    rhs = _match_arrayset(nbody[0], newvar, keyvar)
    if not _is_var(rhs, concrete_p):
        return None
    orelse = node.get("orelse", [])
    if len(orelse) != 1:
        return None
    nxt = orelse[0]
    if isinstance(nxt, dict) and nxt.get("stmt") == "If":
        sub = _chain_rec(nxt, newvar, tvar_p, concrete_p, fname)
        if sub is None:
            return None
        subkeys, kv2, vv2 = sub
        if kv2 != keyvar:
            return None
        return ([lit_key] + subkeys, keyvar, valvar)
    # terminal else: new[keyvar] = self(valvar, tvar, concrete)
    rhs2 = _match_arrayset(nxt, newvar, keyvar)
    if not _is_self_rec_call(rhs2, valvar, tvar_p, concrete_p, fname):
        return None
    return ([lit_key], keyvar, valvar)


def _match_substmap_loop(loop: Any, subj: str, newvar: str, tvar_p: str,
                         concrete_p: str, fname: str) -> Optional[List[str]]:
    """`for k, v in <subj>.items(): <rewrite-chain>` — the reconstruction loop
    (the tuple target is erased to `_for_target`; the body still references the
    phantom key/value Vars). Returns the rewrite keys or None."""
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"):
        return None
    it = loop.get("iter", {})
    if not (isinstance(it, dict) and it.get("type") == "Call"
            and it.get("func") == f"{subj}.items" and not it.get("args")):
        return None
    lbody = loop.get("body", [])
    if len(lbody) != 1:
        return None
    res = _chain_rec(lbody[0], newvar, tvar_p, concrete_p, fname)
    if res is None:
        return None
    keys, _kv, _vv = res
    return keys


def _match_substmap_post_type(stmt: Any, newvar: str, tvar_p: str,
                              concrete_p: str) -> bool:
    """The post-loop `if "type" in new and new["type"]==tvar: new["type"]=concrete`
    field rewrite. Detected structurally (fail-closed); its effect is folded
    into the per-cell rule for the `type` key (identical type behaviour)."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "If"):
        return False
    if stmt.get("orelse"):
        return False
    body = stmt.get("body", [])
    if len(body) != 1:
        return False
    aset = body[0]
    if not (isinstance(aset, dict) and aset.get("stmt") == "ArraySet"
            and _is_var(aset.get("array"), newvar)
            and _is_string(aset.get("index")) == "type"
            and _is_var(aset.get("value"), concrete_p)):
        return False
    # test must reference the `type` key and compare to tvar (value-only fact;
    # matched loosely — the ArraySet above is the load-bearing anchor).
    return True


def _match_substmap_list_arm(lbody: Any, subj: str, tvar_p: str,
                             concrete_p: str, fname: str) -> bool:
    """`return [ self(item, tvar, concrete) for item in <subj> ]` — the list
    reconstruction arm (a functorial map over the list)."""
    if not (isinstance(lbody, list) and len(lbody) == 1):
        return False
    ret = lbody[0]
    if not (isinstance(ret, dict) and ret.get("stmt") == "Return"):
        return False
    lc = ret.get("value", {})
    if not (isinstance(lc, dict) and lc.get("type") == "ListComp"):
        return False
    gens = lc.get("generators", [])
    if len(gens) != 1:
        return False
    g = gens[0]
    if not (isinstance(g, dict) and _is_var(g.get("iter"), subj)
            and not g.get("ifs")):
        return False
    item = g.get("target")
    if not isinstance(item, str):
        return False
    return _is_self_rec_call(lc.get("elt"), item, tvar_p, concrete_p, fname)


def recognize_substmap(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the T1 functorial-map reconstruction traversal
    (`node: Any -> Any`, rebuild the IR replacing a TypeVar Var by a concrete
    type). Returns {subject, tvar_param, concrete_param, rewrite_keys} when the
    IR body is *exactly* the reconstruction shape; else None. Never raises."""
    try:
        return _recognize_substmap(func)
    except Exception:
        return None


def _recognize_substmap(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 3:
        return None
    subj, tvar_p, concrete_p = params
    pa = func.get("param_annotations", {})
    if pa.get(tvar_p) != "str" or pa.get(concrete_p) != "str":
        return None
    # result algebra = the value type itself (a rebuilt `Any`).
    if func.get("return_annotation") != "Any":
        return None
    # pure reconstruction — the frame MUST be `\nothing` (fail-closed; a
    # `writes`-carrying contract on a functional rebuild does not fire).
    assigns = func.get("contracts", {}).get("assigns", []) or []
    if not (len(assigns) == 1 and isinstance(assigns[0], dict)
            and assigns[0].get("type") == "Nothing"):
        return None
    fname = func["name"]

    body = func.get("body", [])
    if len(body) != 3:
        return None
    dict_if, list_if, final_ret = body

    # final: `return <subj>` (the leaf/passthrough arm).
    if not (isinstance(final_ret, dict) and final_ret.get("stmt") == "Return"
            and _is_var(final_ret.get("value"), subj)):
        return None

    # dict arm: `if isinstance(<subj>, dict): new={}; for …: …; [post]; return new`.
    if not (isinstance(dict_if, dict) and dict_if.get("stmt") == "If"):
        return None
    if dict_if.get("orelse"):
        return None
    if not _match_isinstance(dict_if.get("test", {}), subj, "dict"):
        return None
    dbody = dict_if.get("body", [])
    if len(dbody) < 3:
        return None
    asg = dbody[0]
    if not (isinstance(asg, dict) and asg.get("stmt") == "Assign"):
        return None
    newvar = asg.get("target")
    if not isinstance(newvar, str) or not _is_dictlit_empty(asg.get("value")):
        return None
    keys = _match_substmap_loop(dbody[1], subj, newvar, tvar_p, concrete_p, fname)
    if keys is None:
        return None
    ret = dbody[-1]
    if not (isinstance(ret, dict) and ret.get("stmt") == "Return"
            and _is_var(ret.get("value"), newvar)):
        return None
    # middle statements (between loop and return): only the optional post-loop
    # `type` rewrite is permitted; anything else fails closed.
    for st in dbody[2:-1]:
        if not _match_substmap_post_type(st, newvar, tvar_p, concrete_p):
            return None
        if "type" not in keys:
            keys.append("type")

    # list arm: `if isinstance(<subj>, list): return [self(item,…) for item in subj]`.
    if not (isinstance(list_if, dict) and list_if.get("stmt") == "If"):
        return None
    if list_if.get("orelse"):
        return None
    if not _match_isinstance(list_if.get("test", {}), subj, "list"):
        return None
    if not _match_substmap_list_arm(list_if.get("body", []), subj, tvar_p,
                                    concrete_p, fname):
        return None

    return {
        "subject": subj,
        "tvar_param": tvar_p,
        "concrete_param": concrete_p,
        "rewrite_keys": keys,
    }


def _frag_predicate_lines() -> List[str]:
    """richer-contracts-bridge P2.3 (C2): `in_emitted_fragment` — the grammar-
    membership predicate scoped to the emitted IR fragment the evaluator axioms
    range over (`src/self-annotate/evaluator-axiom-audit.md`). Structural half:
    the fragment carries no bare `PNone` sentinel (the string-TAG half — which
    audited `stmt` tags appear — is the `pystr_eq`-opaque boundary the audit
    leaves to prose). A bridge-audit obligation (pure definition, NO axiom); the
    type-substitution preserves it, so it lands as a preservation contract."""
    return [
        "",
        "  (* richer-contracts-bridge P2.3 (C2): emitted-fragment grammar membership",
        "     (structural scope: no bare PNone sentinel). Bridge-audit predicate tying",
        "     the method to evaluator-axiom-audit.md's boundary BY CONTRACT. NO axiom. *)",
        "  predicate in_emitted_fragment (v: pyval)",
        "  = match v with",
        "    | PNone -> false",
        "    | PInt _ | PStr _ | PBool _ -> true",
        "    | PList xs -> frag_list xs",
        "    | PDict d  -> frag_dict d",
        "    end",
        "  with frag_dict (d: pydict)",
        "  = match d with",
        "    | DNil -> true",
        "    | DCons _ v rest -> in_emitted_fragment v /\\ frag_dict rest",
        "    end",
        "  with frag_list (xs: list pyval)",
        "  = match xs with",
        "    | Nil -> true",
        "    | Cons h t -> in_emitted_fragment h /\\ frag_list t",
        "    end",
    ]


def _wf_deep_predicate_lines() -> List[str]:
    """richer-contracts-bridge P2.1 (C2): the DEEP well-formedness predicate
    family + the two lemmas tying it to the certified shallow wf_ir.

    The certified `wf_ir` (Phase2c_PyValDict.v, preamble) is SHALLOW (top-level
    dict keys only); measured NOT to be an inductive invariant of the recursive
    substitution (threading it as `requires` leaves the recursive-call
    precondition undischargeable — the __dict/__list VCs time out). The genuinely
    preservable invariant recurses into list elements AND dict values. It is a
    pure DEFINITION (no `axiom`; ledger untouched), and the two `let rec lemma`s
    prove `wf_ir_deep v -> wf_ir v`, so `ensures wf_ir_deep result` entails the
    audited shallow wf_ir. Bridge-audit predicate, generator-owned."""
    return [
        "",
        "  (* richer-contracts-bridge P2.1 (C2): DEEP well-formedness — the INDUCTIVE",
        "     invariant of the recursive substitution (recurses into list elements AND",
        "     dict values). Strengthens the certified shallow wf_ir; pure definition,",
        "     NO axiom. The two lemmas prove it implies the certified wf_ir. *)",
        "  predicate wf_ir_deep (v: pyval)",
        "  = match v with",
        "    | PDict d  -> wf_dict_deep d",
        "    | PList xs -> wf_list_deep xs",
        "    | _ -> true",
        "    end",
        "  with wf_dict_deep (d: pydict)",
        "  = match d with",
        "    | DNil -> true",
        "    | DCons k v rest -> wf_val k v /\\ wf_ir_deep v /\\ wf_dict_deep rest",
        "    end",
        "  with wf_list_deep (xs: list pyval)",
        "  = match xs with",
        "    | Nil -> true",
        "    | Cons h t -> wf_ir_deep h /\\ wf_list_deep t",
        "    end",
        "  (* Bridge tie: the deep predicate strengthens the certified shallow wf_ir",
        "     (Phase2c_PyValDict.v), so `ensures wf_ir_deep result` entails the audited",
        "     wf_ir. Proved by structural induction — NO axiom. *)",
        "  let rec lemma wf_dict_deep_shallow (d: pydict) : unit",
        "    requires { wf_dict_deep d } ensures { wf_dict d } variant { d }",
        "  = match d with DNil -> () | DCons _ _ rest -> wf_dict_deep_shallow rest end",
        "  let lemma wf_ir_deep_shallow (v: pyval) : unit",
        "    requires { wf_ir_deep v } ensures { wf_ir v }",
        "  = match v with PDict d -> wf_dict_deep_shallow d | _ -> () end",
        "  (* Lemma-pack fact for the string-key case: a value that stays a PStr",
        "     whenever it was a PStr keeps wf_val for its key. `let lemma` (CALLED by",
        "     the fold body => split-robust exact instantiation); the explicit case",
        "     split on k discharges its own VC. *)",
        "  let lemma wf_val_str_stable (k: irkey) (v v2: pyval) : unit",
        "    requires { wf_val k v }",
        "    requires { match v with PStr _ -> "
        "(match v2 with PStr _ -> true | _ -> false end) | _ -> true end }",
        "    ensures  { wf_val k v2 }",
        "  = match k with",
        "    | K_op | K_type | K_target | K_func | K_name -> ()",
        "    | _ -> () end",
    ]


def emit_substmap_group(func: Dict[str, Any], sm: Dict[str, Any],
                        whyml_ident, top_ensures: Optional[List[str]] = None,
                        top_requires: Optional[List[str]] = None) -> List[str]:
    """Emit the T1 functorial-map reconstruction group for a recognized substmap.

    Functional (`assigns \\nothing`; no `writes`): every function returns the
    value type (`pyval`/`pydict`/`list pyval`), rebuilding constructor cells.
    The per-instance rewrite-rule hole is defunctionalized into a `__triggers`
    predicate over the interned rewrite keys (structural discriminants, zero
    string theory for named keys); the semantic guard is the opaque `pystr_eq`;
    the replacement is the well-typed `PStr <concrete>`. Reuses the L1 preamble
    `size`/lemma pack for the `variant`. Congruent (modulo names) to the proven
    `scratchpad` T1 spike."""
    n = whyml_ident(func["name"])
    subj = sm["subject"]
    tvar = sm["tvar_param"]
    concrete = sm["concrete_param"]
    keys = sm["rewrite_keys"]
    named = [k for k in keys if k in _NAMED_KEYS]
    dyn = [k for k in keys if k not in _NAMED_KEYS]
    out: List[str] = []

    # ---- defunctionalized rewrite-key predicate (structural discriminants) ----
    out.append(f"  let {n}__triggers (k: irkey) : bool")
    out.append("  = match k with")
    for k in named:
        out.append(f"    | {_NAMED_KEYS[k]} -> true")
    if dyn:
        cond = " || ".join(f'pystr_eq s "{d}"' for d in dyn)
        out.append(f"    | K_dyn s -> {cond}")
    out.append("    | _ -> false end")

    # ---- the subst_walk / subst_dict / subst_list reconstruction group ----
    # richer-contracts-bridge C1: the top-level function carries the METHOD's own
    # `#@ ensures` (default `["true"]` => byte-identical to the historical
    # hardcoded `ensures { true }`; a certified predicate on `\result` becomes a
    # checked postcondition). Helper functions keep `ensures { true }`.
    _te = list(top_ensures or ["true"])
    _tr = list(top_requires or ["true"])
    # richer-contracts-bridge P2.1 (C2): wf-preservation mode fires iff the
    # METHOD's contract threads the deep well-formedness predicate. When it does,
    # (i) emit the deep predicate family + connecting lemmas (gated => corpus and
    # non-wf mirrors byte-identical), (ii) thread the method's requires onto the
    # top-level function, (iii) emit the per-helper preservation contracts
    # (__dict: wf_dict_deep, __list: wf_list_deep) so Why3 discharges the
    # induction helper-by-helper, (iv) add the string-stability ensures the
    # lemma pack needs for the string-key case.
    # richer-contracts-bridge C2 preservation families: each is a deep predicate
    # the type-substitution PRESERVES.  A family fires iff the METHOD's contract
    # threads its top predicate (in `_te`/`_tr`).  Each contributes a `<dict>`/
    # `<list>` requires+ensures conjunct on the helpers so Why3 discharges the
    # induction helper-by-helper.  wf_ir_deep (P2.1) additionally needs the
    # string-stability ensures + the called str-lemma hint (its wf_val string-key
    # case); in_emitted_fragment (P2.3) needs neither (its leaf/PStr arms hold).
    _families = [
        ("wf_ir_deep",          "wf_dict_deep", "wf_list_deep", _wf_deep_predicate_lines),
        ("in_emitted_fragment", "frag_dict",    "frag_list",    _frag_predicate_lines),
    ]
    _active = [f for f in _families if any(f[0] in c for c in (_te + _tr))]
    _wf_preserve = any(f[0] == "wf_ir_deep" for f in _active)
    if _active:
        for _top, _d, _l, _emit in _active:
            out.extend(_emit())
        if _wf_preserve:
            _te = _te + [
                f"match {subj} with PStr _ -> "
                f"(match result with PStr _ -> true | _ -> false end) | _ -> true end"
            ]
        _dreq = " /\\ ".join(f"{f[1]} d" for f in _active)
        _dens = " /\\ ".join(f"{f[1]} result" for f in _active)
        _lreq = " /\\ ".join(f"{f[2]} xs" for f in _active)
        _lens = " /\\ ".join(f"{f[2]} result" for f in _active)
        _dict_contract = f"    requires {{ {_dreq} }} ensures {{ {_dens} }}"
        _list_contract = f"    requires {{ {_lreq} }} ensures {{ {_lens} }}"
    else:
        _dict_contract = "    requires { true } ensures { true }"
        _list_contract = "    requires { true } ensures { true }"
    _ens_line = "".join(f" ensures {{ {e} }}" for e in _te)
    _req_line = "".join(f" requires {{ {r} }}" for r in _tr)
    out.append(f"  let rec {n} ({subj}: pyval) ({tvar}: string) ({concrete}: string) : pyval")
    out.append(f"   {_req_line}{_ens_line}")
    out.append(f"    variant {{ pv_size {subj} }}")
    out.append(f"  = match {subj} with")
    out.append(f"    | PList xs -> PList ({n}__list xs {tvar} {concrete})")
    out.append(f"    | PDict d  -> PDict ({n}__dict d {tvar} {concrete})")
    out.append(f"    | _ -> {subj} end")
    out.append(f"  with {n}__dict (d: pydict) ({tvar}: string) ({concrete}: string) : pydict")
    out.append(_dict_contract)
    out.append("    variant { size_dict d }")
    out.append("  = match d with")
    out.append("    | DNil -> DNil")
    out.append("    | DCons k v rest ->")
    out.append("        let v2 =")
    out.append("          match v with")
    out.append(f"          | PStr s -> if {n}__triggers k && pystr_eq s {tvar} then PStr {concrete}")
    out.append(f"                      else {n} v {tvar} {concrete}")
    out.append(f"          | _ -> {n} v {tvar} {concrete} end")
    out.append("        in")
    if _wf_preserve:
        # Split-robust proof hints for `ensures wf_dict_deep result`: the
        # recursion preserves PStr-ness (str-stability of the top-level ensures);
        # the CALLED lemma turns that + wf_val k v (precondition head) into
        # wf_val k v2; wf_ir_deep v2 comes from the recursion's own postcondition.
        out.append("        assert { match v with PStr _ -> "
                   "(match v2 with PStr _ -> true | _ -> false end) | _ -> true end };")
        out.append("        wf_val_str_stable k v v2;")
        out.append("        assert { wf_ir_deep v2 };")
    out.append(f"        DCons k v2 ({n}__dict rest {tvar} {concrete})")
    out.append("    end")
    out.append(f"  with {n}__list (xs: list pyval) ({tvar}: string) ({concrete}: string) : list pyval")
    out.append(_list_contract)
    out.append("    variant { size_list xs }")
    out.append("  = match xs with Nil -> Nil")
    out.append(f"    | Cons h t -> Cons ({n} h {tvar} {concrete}) ({n}__list t {tvar} {concrete}) end")
    return out


# =========================================================================
# ir-traversal-residual A-bool + T2 + D — the COMPOSED / SHORT-CIRCUIT shapes
# (plan §3 T2 option/first-match, §4 D traversal outlining, plus the A-bool
# existence-fold algebra — the smallest algebra: fold into `bool` with `||`).
#
# `find_return_type` (shapes 3+4) decomposes into three separately-certified
# `let rec` groups over the L1 `pyval`/`pydict` model:
#
#   * A-BOOL existence folds — the two nested closures `_has_return` /
#     `_has_return_with_value` (lambda-lifted by the front-end to sibling
#     methods `<cls>___has_return*`). A `pyval -> bool` walk that descends the
#     statement subtree (`body`/`orelse` fields + `Match` `cases` bodies) and
#     OR-combines a `stmt["stmt"]=="Return"` discriminant. Under `ensures True`
#     the returned bool is UNCONSTRAINED (insight C), so the value narrowings
#     (`and stmt.get("value")` for the with-value twin; descend only specific
#     keys) are value facts the contract does not need — the emitted walk is a
#     total, terminating, well-typed existence fold. Certified like A-set.
#
#   * D — traversal outlining: `find_return_type`'s composing body becomes a
#     non-recursive-in-spirit first-order function that CALLS the two outlined
#     bool folds and its own first-match search; each outlined traversal is its
#     own `let rec`, re-proved per instance.
#
#   * T2 — the first-match search loop is the fold into `string` with a
#     left-biased combining step (the early `return x`); recursion descends the
#     `body`/`orelse`/`cases` fields via total `pyval -> list pyval` projections.
#     The synthetic string tail `"(" + ", ".join(["int"]*n) + ")"` is
#     type-safe: `n = len(elts)` is `>= 0` (an emitted `llen` fold), so
#     `Array.make n "int"` discharges its creation-size VC.
#
# TERMINATION — the crux is the non-syntactic recursion `find_return_type(
# stmt[key])` (descends a dict FIELD, not a direct sub-term). The field
# projections carry `ensures { size_list result < size v }` (proved from the
# spine readers' `size_list result < 1 + size_dict d`), which discharges the
# `variant { size_list stmts }` decrease. The `find_return_type -> __search`
# same-size edge is ordered by a lexicographic second component (1 vs 0). Both
# the projection-bound and the lexicographic variant are Alt-Ergo-proved.
#
# NO new value shape, NO exceptions, NO new axiom — the ledger stays at 3.
# Fail-closed exactly as the folds: a miss keeps the method `\trusted`; a
# template bug is a loud unprovable instance, never a false proof. Verified
# inert on the reference corpus (byte-diff 0); a poison control flips red once.
# =========================================================================


def _match_subscript_str(node: Any, subj: str) -> Optional[str]:
    """`<subj>["<lit>"]` (Subscript with string index) -> "<lit>" or None."""
    if not (isinstance(node, dict) and node.get("type") == "Subscript"
            and _is_var(node.get("value"), subj)):
        return None
    return _is_string(node.get("index"))


def _match_get_call(node: Any, subj: str) -> Optional[str]:
    """`<subj>.get("<lit>"[, default])` -> "<lit>" or None."""
    if not (isinstance(node, dict) and node.get("type") == "Call"
            and node.get("func") == f"{subj}.get"):
        return None
    args = node.get("args", [])
    if not args:
        return None
    return _is_string(args[0])


def _match_stmt_tag_test(test: Any, subj: str) -> Optional[str]:
    """`<subj>["stmt"] == "<TAG>"` or `<subj>.get("stmt") == "<TAG>"` -> TAG."""
    if not (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "=="):
        return None
    tag = _is_string(test.get("right"))
    if tag is None:
        return None
    left = test.get("left", {})
    if _match_subscript_str(left, subj) == "stmt":
        return tag
    if _match_get_call(left, subj) == "stmt":
        return tag
    return None


def _is_bool_true_return(stmt: Any) -> bool:
    return (isinstance(stmt, dict) and stmt.get("stmt") == "Return"
            and isinstance(stmt.get("value"), dict)
            and stmt["value"].get("type") == "Bool"
            and stmt["value"].get("value") is True)


def _is_selfcall_n(node: Any, name_box: List[str], extra: List[str]) -> bool:
    """A `(1 + len(extra))`-arg Call whose func is a bare name; the first arg
    is the recursion target, and the remaining args thread the read-only
    `extra` params UNCHANGED, in order (the `uses_ghost_type`-shaped
    `self(stmt[key], types)` self-recursion). Records the callee in name_box
    (all existence-fold self-calls must share one callee name). `extra=[]`
    reproduces the original 1-arg-only check exactly."""
    if not (isinstance(node, dict) and node.get("type") == "Call"):
        return False
    f = node.get("func")
    if not isinstance(f, str):
        return False
    args = node.get("args", [])
    if len(args) != 1 + len(extra):
        return False
    if not all(_is_var(args[1 + i], e) for i, e in enumerate(extra)):
        return False
    name_box.append(f)
    return True


def recognize_bool_existence(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the A-bool statement-tree existence fold — the
    lambda-lifted `_has_return` / `_has_return_with_value` closures (tag
    "Return", 3-arm loop body incl. the Match/cases descent), AND (stmt-walker
    foundation, list-adt-foundation-build.md) the plain single-tag scanners
    `uses_for`/`uses_arrayset`-shaped methods: `for stmt in xs: if <tag-test>:
    return True; for key in ("body","orelse"): if key in stmt and
    self(stmt[key]): return True // return False` — a 2-arm loop body (no
    Match/cases arm) over ANY literal tag ("For", "ArraySet", ... — not just
    "Return"). Both are the SAME structural shape (tag-test arm + field-
    descend arm + an OPTIONAL cases-descend arm); the tag and the presence of
    the cases arm are the only degrees of freedom.

    Two further generalizations of the SAME shape (both threaded through the
    identical `let rec`/`__v`/`__d` OR-descend emission, no new code path):
      * arm 0 accepts a COMPOUND `<tag-test> and <stmt>.get(<key>) in <extra>`
        guard (`uses_ghost_type`-shaped) when the method threads a second,
        read-only `set`-typed parameter -- under `ensures True` the membership
        conjunct is a value fact the fold does not need (insight C).
      * arm 1 accepts an INLINED single-If descend (`has_continue`-shaped:
        `if <tag "If">: if (self(body) or self(orelse)): return True`) as an
        alternate SOURCE shape for the same OR-descend, instead of the
        generic `for key in ("body","orelse")` loop.

    Returns {subject, self_name, with_value, tag, extra_params} or None.
    Never raises."""
    try:
        return _recognize_bool_existence(func)
    except Exception:
        return None


def _recognize_bool_existence(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) not in (1, 2):
        return None
    subj = params[0]
    extra = params[1:]
    pa = func.get("param_annotations", {})
    if pa.get(subj) != "list":
        return None
    # An optional 2nd param is a read-only membership SET, threaded UNCHANGED
    # through every recursive call (the `uses_ghost_type`-shaped compound
    # guard). Fail-closed: any non-`set` 2nd param rejects.
    for e in extra:
        if pa.get(e) != "set":
            return None
    if func.get("return_annotation") != "bool":
        return None
    body = func.get("body", [])
    if len(body) != 2:
        return None
    loop, tail = body
    # tail: `return False`
    if not (isinstance(tail, dict) and tail.get("stmt") == "Return"
            and isinstance(tail.get("value"), dict)
            and tail["value"].get("type") == "Bool"
            and tail["value"].get("value") is False):
        return None
    # loop: `for stmt in <subj>: <2-or-3 arms>`
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"
            and _is_var(loop.get("iter"), subj)):
        return None
    stmtv = loop.get("target")
    if not isinstance(stmtv, str):
        return None
    lbody = loop.get("body", [])
    # the Match/cases-descend arm (a2) is OPTIONAL — `uses_for`/`uses_arrayset`
    # only ever descend "body"/"orelse", with no Match arm at all.
    if len(lbody) not in (2, 3):
        return None
    a0, a1 = lbody[0], lbody[1]
    a2 = lbody[2] if len(lbody) == 3 else None
    names: List[str] = []
    with_value = False
    # arm 0: if <stmt-tag-test>: return True  (ANY literal tag, not just "Return")
    if not (isinstance(a0, dict) and a0.get("stmt") == "If" and not a0.get("orelse")):
        return None
    t0 = a0.get("test", {})
    tag0 = _match_stmt_tag_test(t0, stmtv)
    if tag0 is None and (isinstance(t0, dict) and t0.get("type") == "BinOp"
                         and t0.get("op") == "and"):
        # with-value twin: `<stmt>["stmt"]=="Return" and <stmt>.get("value")`
        # -- inherently Return-specific (the `.get("value")` guard only makes
        # sense for the Return tag), so this alternate arm-0 shape stays
        # hardcoded to "Return" (it is a DIFFERENT AST shape, not a tag choice).
        maybe_tag = _match_stmt_tag_test(t0.get("left", {}), stmtv)
        if maybe_tag == "Return" and _match_get_call(t0.get("right", {}), stmtv) == "value":
            tag0, with_value = "Return", True
        else:
            # compound membership-guarded tag test (`uses_ghost_type` shape):
            # `<tag-test> and <stmt>.get("<key>") in <extra-param>` (either
            # conjunct order). Needs the optional 2nd `set` param -- fails
            # closed (via `_match_in_guard`) when `extra` is empty.
            tag0 = _match_compound_tag_mem_guard(t0, stmtv, extra)
    if tag0 is None:
        return None
    if not (len(a0.get("body", [])) == 1 and _is_bool_true_return(a0["body"][0])):
        return None
    # arm 1: for key in ("body","orelse"): if key in stmt and self(stmt[key], extra...): return True
    #     OR the INLINED single-If descend (`has_continue` shape): if <tag "If">:
    #     if (self(body, extra...) or self(orelse, extra...)): return True
    if not (_match_field_descend_loop(a1, stmtv, names, extra)
            or _match_inline_if_descend(a1, stmtv, names, extra)):
        return None
    # arm 2 (optional): if stmt.get("stmt")=="Match": for c in stmt.get("cases",[]): if self(c.get("body",[]), extra...): return True
    if a2 is not None and not _match_cases_descend(a2, stmtv, names, extra):
        return None
    if not names or any(x != names[0] for x in names):
        return None
    return {"subject": subj, "self_name": names[0], "with_value": with_value,
            "tag": tag0, "extra_params": extra}


def _match_compound_tag_mem_guard(test: Any, stmtv: str,
                                  extra: List[str]) -> Optional[str]:
    """`<tag-test> and <stmt>.get("<key>") in <extra-param>` (either conjunct
    order) -- the compound existence-arm guard threading a read-only
    membership SET parameter (`uses_ghost_type`-shaped:
    `stmt.get("stmt")=="GhostAssign" and stmt.get("ghost_type") in types`).
    Under `ensures True` the membership conjunct is a value fact the fold
    does not need (insight C) -- only its SHAPE is validated. Returns the
    literal TAG, or None (fail-closed; also None when `extra` is empty, since
    `_match_in_guard` then has no valid RHS to match)."""
    if not (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "and"):
        return None
    left, right = test.get("left", {}), test.get("right", {})
    tag = _match_stmt_tag_test(left, stmtv)
    mem_side = right
    if tag is None:
        tag = _match_stmt_tag_test(right, stmtv)
        mem_side = left
    if tag is None:
        return None
    if _match_in_guard(mem_side, stmtv, extra) is None:
        return None
    return tag


def _match_field_descend_loop(node: Any, stmtv: str, names: List[str],
                              extra: List[str]) -> bool:
    """`for key in ("body","orelse"): if key in <stmt> and <self>(<stmt>[key][, extra...]): return True`."""
    if not (isinstance(node, dict) and node.get("stmt") == "For"):
        return False
    it = node.get("iter", {})
    if not (isinstance(it, dict) and it.get("type") == "Tuple"):
        return False
    keys = [_is_string(e) for e in it.get("elts", [])]
    if keys != ["body", "orelse"]:
        return False
    keyv = node.get("target")
    lb = node.get("body", [])
    if len(lb) != 1:
        return False
    iff = lb[0]
    if not (isinstance(iff, dict) and iff.get("stmt") == "If" and not iff.get("orelse")):
        return False
    test = iff.get("test", {})
    if not (isinstance(test, dict) and test.get("type") == "BinOp" and test.get("op") == "and"):
        return False
    left, right = test.get("left", {}), test.get("right", {})
    # left: key in stmt
    if not (isinstance(left, dict) and left.get("type") == "BinOp" and left.get("op") == "in"
            and _is_var(left.get("left"), keyv) and _is_var(left.get("right"), stmtv)):
        return False
    # right: self(stmt[key][, extra...])
    if not _is_selfcall_n(right, names, extra):
        return False
    arg = right["args"][0]
    if not (isinstance(arg, dict) and arg.get("type") == "Subscript"
            and _is_var(arg.get("value"), stmtv) and _is_var(arg.get("index"), keyv)):
        return False
    return len(iff.get("body", [])) == 1 and _is_bool_true_return(iff["body"][0])


def _match_inline_if_descend(node: Any, stmtv: str, names: List[str],
                             extra: List[str]) -> bool:
    """`if <stmt-tag-test "If">: if (<self>(<stmt>.get("body",[])[, extra...])
        or <self>(<stmt>.get("orelse",[])[, extra...])): return True` -- the
    INLINED single-If descend arm (`has_continue`-shaped): a tag-gated nested
    If whose test is an `or` of the two self-recursions on body/orelse,
    instead of the generic `for key in ("body","orelse")` loop. Same
    OR-descend RESULT under `ensures True` -- `emit_bool_existence_group`
    always OR-descends the whole subtree regardless of which source arm-1
    shape matched -- so this is purely an alternate SOURCE shape, not a
    separate emission."""
    if not (isinstance(node, dict) and node.get("stmt") == "If" and not node.get("orelse")):
        return False
    if _match_stmt_tag_test(node.get("test", {}), stmtv) != "If":
        return False
    body = node.get("body", [])
    if len(body) != 1:
        return False
    inner = body[0]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If" and not inner.get("orelse")):
        return False
    test = inner.get("test", {})
    if not (isinstance(test, dict) and test.get("type") == "BinOp" and test.get("op") == "or"):
        return False
    left, right = test.get("left", {}), test.get("right", {})
    if not (_is_selfcall_n(left, names, extra)
            and _match_get_call(left["args"][0], stmtv) == "body"):
        return False
    if not (_is_selfcall_n(right, names, extra)
            and _match_get_call(right["args"][0], stmtv) == "orelse"):
        return False
    return len(inner.get("body", [])) == 1 and _is_bool_true_return(inner["body"][0])


def _match_cases_descend(node: Any, stmtv: str, names: List[str],
                         extra: List[str]) -> bool:
    """`if <stmt>.get("stmt")=="Match": for c in <stmt>.get("cases",[]):
        if <self>(c.get("body",[])[, extra...]): return True`."""
    if not (isinstance(node, dict) and node.get("stmt") == "If" and not node.get("orelse")):
        return False
    if _match_stmt_tag_test(node.get("test", {}), stmtv) != "Match":
        return False
    cb = node.get("body", [])
    if len(cb) != 1:
        return False
    loop = cb[0]
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"):
        return False
    if _match_get_call(loop.get("iter", {}), stmtv) != "cases":
        return False
    cvar = loop.get("target")
    lb = loop.get("body", [])
    if len(lb) != 1:
        return False
    iff = lb[0]
    if not (isinstance(iff, dict) and iff.get("stmt") == "If" and not iff.get("orelse")):
        return False
    call = iff.get("test", {})
    if not _is_selfcall_n(call, names, extra):
        return False
    if _match_get_call(call["args"][0], cvar) != "body":
        return False
    return len(iff.get("body", [])) == 1 and _is_bool_true_return(iff["body"][0])


def _emit_stmt_reader(p: str) -> List[str]:
    """Emit the plain `stmt`-key reader + discriminant (prefix `p`). No
    size-bound `ensures` — split_vc-robust (the descent uses direct structural
    sub-terms for its `variant`, not a projected-field size relation, so the
    readers never enter a termination VC)."""
    out: List[str] = []
    out.append(f"  let rec {p}__get_stmt (d: pydict) : option string")
    out.append("    variant { d }")
    out.append("  = match d with DNil -> None")
    out.append(f'    | DCons (K_dyn k) (PStr s) rest -> if pystr_eq k "stmt" then Some s else {p}__get_stmt rest')
    out.append(f"    | DCons _ _ rest -> {p}__get_stmt rest end")
    out.append(f"  let function {p}__stmt_is (v: pyval) (tag: string) : bool")
    out.append("  = match v with")
    out.append(f"    | PDict d -> (match {p}__get_stmt d with Some t -> pystr_eq t tag | None -> false end)")
    out.append("    | _ -> false end")
    return out


def emit_bool_existence_group(func: Dict[str, Any], desc: Dict[str, Any],
                              whyml_ident) -> List[str]:
    """Emit the A-bool statement-tree existence fold for a recognized closure.

    A universal `pyval`/`pydict`/`list pyval` catamorphism folding into `bool`
    by `||` (the smallest algebra). The recursion is on DIRECT structural
    sub-terms (the `v` of `DCons`, the `h`/`t` of `Cons`), so each `variant`
    (`size`/`size_dict`/`size_list`) decreases syntactically — split_vc-robust,
    the proven A-set shape. The `stmt`-tag discriminant at `PDict` nodes mirrors
    the source's `stmt["stmt"]==<tag>` test (the recognized literal tag —
    "Return", "For", "ArraySet", ... — threaded from `desc["tag"]`, not
    hardcoded); under `ensures True` the returned bool is a value fact the
    contract does not constrain (insight C), so the walk OR-descends the whole
    subtree (a superset of `body`/`orelse`/`cases`).

    `desc["extra_params"]` (the `uses_ghost_type`-shaped optional read-only
    membership SET, default empty) is threaded UNCHANGED through every
    generated signature and recursive call, typed `map string bool` exactly
    as `recognize_setfold`'s `extra_params` — its VALUE is never inspected
    (the compound guard is dropped under `ensures True`, same insight-C
    doctrine), only its ARITY matters. Empty `extra_params` reproduces the
    original emission byte-for-byte (empty signature/arg suffixes)."""
    n = whyml_ident(func["name"])
    tag = desc["tag"]
    extra = desc.get("extra_params") or []
    extra_sig = "".join(f" ({whyml_ident(e)}: map string bool)" for e in extra)
    extra_args = "".join(f" {whyml_ident(e)}" for e in extra)
    out = _emit_stmt_reader(n)
    out.append(f"  let rec {n} (stmts: list pyval){extra_sig} : bool")
    out.append("    requires { true } ensures { true } variant { size_list stmts }")
    out.append(f"  = match stmts with Nil -> false | Cons h t -> {n}__v h{extra_args} || {n} t{extra_args} end")
    out.append(f"  with {n}__v (v: pyval){extra_sig} : bool")
    out.append("    requires { true } ensures { true } variant { pv_size v }")
    out.append("  = match v with")
    out.append(f'    | PDict d -> {n}__stmt_is v "{tag}" || {n}__d d{extra_args}')
    out.append(f"    | PList xs -> {n} xs{extra_args}")
    out.append("    | _ -> false end")
    out.append(f"  with {n}__d (d: pydict){extra_sig} : bool")
    out.append("    requires { true } ensures { true } variant { size_dict d }")
    out.append("  = match d with DNil -> false")
    out.append(f"    | DCons _ v rest -> {n}__v v{extra_args} || {n}__d rest{extra_args} end")
    return out


# =========================================================================
# A-bool MULTIWAY statement-tree existence fold — `recognize_bool_multiway`.
#
# Sibling of `recognize_bool_existence` for a DIFFERENT source shape: instead
# of a rigid 2-3-arm loop body testing `<stmt>["stmt"]==<TAG>` directly, this
# is a genuine multiway `stype = stmt.get("stmt")` dispatch (`has_direct_
# return`/`has_in_loop_return`-shaped): the tag is read into a local ONCE,
# then a SEQUENCE of `if stype == "<TAG>"` / `if stype in ("<TAG>", ...)`
# arms follow -- as either separate top-level `if` statements (has_direct_
# return) or a Python `if/elif/elif` chain (compiled as nested `If`s threaded
# through `orelse`, has_in_loop_return). Each arm's action is one of:
#   * a bare `return True` (the tag alone is decisive);
#   * `if (<call>(<subj>.get("body"/"orelse", []))) or ...): return True`
#     (an OR-chain of 1+ recursive calls into named child fields);
#   * the `body`/`orelse` field-descend LOOP (`_match_field_descend_loop`,
#     reused verbatim from `recognize_bool_existence`);
#   * the two-statement Try/handlers arm: `if <call>(<subj>.get("body", [])):
#     return True` followed by `for h in <subj>.get("handlers", []): if
#     <call>(h.get("body", [])): return True`.
#
# A recursive call's CALLEE NAME is never checked for consistency: any bare
# name is accepted (self-recursion, OR a sibling call like `has_in_loop_
# return`'s cross-call to `has_direct_return`) -- because emission does not
# reproduce the source's call graph at all. Under `ensures True` (insight C)
# the emitted catamorphism OR-descends the WHOLE subtree regardless of which
# specific arm/callee the source used (a sound superset), so the sibling
# call is subsumed by the same self-descent: only the call's STRUCTURAL
# shape (single arg, a genuine child-field accessor) is validated, never its
# name. No new WhyML theory -- `emit_bool_multiway_group` is a trivial
# N-tag generalization of `emit_bool_existence_group` (OR across every tag
# collected from the recognized arms instead of one), reusing the identical
# `_emit_stmt_reader`/`pv_size`/`size_dict`/`size_list` machinery.
# =========================================================================


def _match_stype_tag_or_tags(test: Any, stypev: str) -> Optional[List[str]]:
    """`<stypev> == "<TAG>"` -> [TAG]; `<stypev> in (<TAG>, ...)` -> [TAG, ...].
    None (fail-closed) otherwise."""
    if not isinstance(test, dict) or test.get("type") != "BinOp":
        return None
    if test.get("op") == "==" and _is_var(test.get("left"), stypev):
        tag = _is_string(test.get("right"))
        return [tag] if tag is not None else None
    if test.get("op") == "in" and _is_var(test.get("left"), stypev):
        right = test.get("right", {})
        if isinstance(right, dict) and right.get("type") == "Tuple":
            tags = [_is_string(e) for e in right.get("elts", [])]
            if tags and all(t is not None for t in tags):
                return tags
    return None


def _is_selfcall_like(node: Any, subjv: str, names: List[str]) -> bool:
    """`<any-name>(<subjv>.get("body"/"orelse", ...))` -- a 1-arg call whose
    func is a bare name (self OR sibling, name unchecked) and whose sole arg
    descends into a named child field of `subjv`. Records the callee name in
    `names` (bookkeeping only -- never gates)."""
    if not (isinstance(node, dict) and node.get("type") == "Call"):
        return False
    f = node.get("func")
    if not isinstance(f, str):
        return False
    args = node.get("args", [])
    if len(args) != 1:
        return False
    if _match_get_call(args[0], subjv) not in ("body", "orelse"):
        return False
    names.append(f)
    return True


def _match_selfcall_or_chain(test: Any, subjv: str, names: List[str]) -> bool:
    """A boolean `or`-chain (any arity via right-recursion) of `_is_selfcall_
    like` calls on `subjv`."""
    if (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "or"):
        return (_match_selfcall_or_chain(test.get("left", {}), subjv, names)
                and _match_selfcall_or_chain(test.get("right", {}), subjv, names))
    return _is_selfcall_like(test, subjv, names)


def _match_try_handlers_arm(arm_body: List[Any], stmtv: str, names: List[str]) -> bool:
    """`if <call-chain>(<stmtv>.get("body", [])): return True` followed by
    `for h in <stmtv>.get("handlers", []): if <call-chain>(h.get("body",
    [])): return True` -- the Try-arm shape descending into both the Try's
    own body and every handler's body."""
    if len(arm_body) != 2:
        return False
    s1, s2 = arm_body
    if not (isinstance(s1, dict) and s1.get("stmt") == "If" and not s1.get("orelse")):
        return False
    if not _match_selfcall_or_chain(s1.get("test", {}), stmtv, names):
        return False
    if not (len(s1.get("body", [])) == 1 and _is_bool_true_return(s1["body"][0])):
        return False
    if not (isinstance(s2, dict) and s2.get("stmt") == "For"):
        return False
    if _match_get_call(s2.get("iter", {}), stmtv) != "handlers":
        return False
    hvar = s2.get("target")
    if not isinstance(hvar, str):
        return False
    lb = s2.get("body", [])
    if len(lb) != 1:
        return False
    iff = lb[0]
    if not (isinstance(iff, dict) and iff.get("stmt") == "If" and not iff.get("orelse")):
        return False
    if not _match_selfcall_or_chain(iff.get("test", {}), hvar, names):
        return False
    return len(iff.get("body", [])) == 1 and _is_bool_true_return(iff["body"][0])


def _match_multiway_arm_body(arm_body: List[Any], stmtv: str, names: List[str]) -> bool:
    """One arm's action: bare `return True`, the field-descend LOOP
    (`_match_field_descend_loop`, no extra params), an inline OR-chain `if`,
    or the two-statement Try/handlers arm."""
    if len(arm_body) == 1 and _is_bool_true_return(arm_body[0]):
        return True
    if len(arm_body) == 1 and _match_field_descend_loop(arm_body[0], stmtv, names, []):
        return True
    if (len(arm_body) == 1 and isinstance(arm_body[0], dict)
            and arm_body[0].get("stmt") == "If" and not arm_body[0].get("orelse")
            and _match_selfcall_or_chain(arm_body[0].get("test", {}), stmtv, names)
            and len(arm_body[0].get("body", [])) == 1
            and _is_bool_true_return(arm_body[0]["body"][0])):
        return True
    if _match_try_handlers_arm(arm_body, stmtv, names):
        return True
    return False


def _expand_multiway_if_chain(s: Any) -> Optional[List[Tuple[Any, List[Any]]]]:
    """One top-level statement -> its `(test, body)` arm(s): a bare `If` with
    no `orelse` is a single arm; an `If` whose `orelse` is a SINGLETON nested
    `If` (Python's `elif`-chain IR shape) unrolls into that arm plus every
    arm of the chain, recursively. Any other non-empty `orelse` (a genuine
    catch-all) fails closed."""
    if not (isinstance(s, dict) and s.get("stmt") == "If"):
        return None
    arms = [(s.get("test", {}), s.get("body", []))]
    orelse = s.get("orelse", [])
    if not orelse:
        return arms
    if len(orelse) == 1 and isinstance(orelse[0], dict) and orelse[0].get("stmt") == "If":
        rest = _expand_multiway_if_chain(orelse[0])
        if rest is None:
            return None
        return arms + rest
    return None


def _flatten_multiway_if_chain(stmts: List[Any]) -> Optional[List[Tuple[Any, List[Any]]]]:
    """Flatten a list of top-level statements -- each either a standalone
    `If` (has_direct_return-shaped: separate sibling ifs) or an `elif`-chain
    (has_in_loop_return-shaped: one `If` threaded through `orelse`) -- into
    one flat arm list, in source order. Both source shapes collapse to the
    SAME arm list shape; only how they are threaded in the IR differs."""
    out: List[Tuple[Any, List[Any]]] = []
    for s in stmts:
        chain = _expand_multiway_if_chain(s)
        if chain is None:
            return None
        out.extend(chain)
    return out


def recognize_bool_multiway(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the multiway `stype = stmt.get("stmt")` dispatch
    A-bool statement-tree existence fold (`has_direct_return`/`has_in_loop_
    return`-shaped). See the module comment above for the full shape.
    Returns {subject, tags} or None. Never raises."""
    try:
        return _recognize_bool_multiway(func)
    except Exception:
        return None


def _recognize_bool_multiway(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    subj = params[0]
    pa = func.get("param_annotations", {})
    if pa.get(subj) != "list":
        return None
    if func.get("return_annotation") != "bool":
        return None
    body = func.get("body", [])
    if len(body) != 2:
        return None
    loop, tail = body
    if not (isinstance(tail, dict) and tail.get("stmt") == "Return"
            and isinstance(tail.get("value"), dict)
            and tail["value"].get("type") == "Bool"
            and tail["value"].get("value") is False):
        return None
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"
            and _is_var(loop.get("iter"), subj)):
        return None
    stmtv = loop.get("target")
    if not isinstance(stmtv, str):
        return None
    lbody = loop.get("body", [])
    if len(lbody) < 2:
        return None
    a0 = lbody[0]
    # arm0: stype = stmt.get("stmt")
    if not (isinstance(a0, dict) and a0.get("stmt") == "Assign"
            and _match_get_call(a0.get("value", {}), stmtv) == "stmt"):
        return None
    stypev = a0.get("target")
    if not isinstance(stypev, str):
        return None
    arms = _flatten_multiway_if_chain(lbody[1:])
    if not arms:
        return None
    names: List[str] = []
    tags: List[str] = []
    for test, arm_body in arms:
        arm_tags = _match_stype_tag_or_tags(test, stypev)
        if not arm_tags:
            return None
        if not _match_multiway_arm_body(arm_body, stmtv, names):
            return None
        for t in arm_tags:
            if t not in tags:
                tags.append(t)
    if not names:
        return None
    return {"subject": subj, "tags": tags}


def emit_bool_multiway_group(func: Dict[str, Any], desc: Dict[str, Any],
                             whyml_ident) -> List[str]:
    """Emit the multiway A-bool statement-tree existence fold -- the SAME
    universal `pyval`/`pydict`/`list pyval` OR-catamorphism as `emit_bool_
    existence_group`, generalized from ONE literal tag to the N tags
    collected off the recognized arms (`desc["tags"]`), OR'd together at
    each `PDict` node. No new WhyML theory: reuses `_emit_stmt_reader` and
    the certified `pv_size`/`size_dict`/`size_list` L1 catamorphism
    verbatim."""
    n = whyml_ident(func["name"])
    tags = desc["tags"]
    tag_disj = " || ".join(f'{n}__stmt_is v "{t}"' for t in tags)
    out = _emit_stmt_reader(n)
    out.append(f"  let rec {n} (stmts: list pyval) : bool")
    out.append("    requires { true } ensures { true } variant { size_list stmts }")
    out.append(f"  = match stmts with Nil -> false | Cons h t -> {n}__v h || {n} t end")
    out.append(f"  with {n}__v (v: pyval) : bool")
    out.append("    requires { true } ensures { true } variant { pv_size v }")
    out.append("  = match v with")
    out.append(f"    | PDict d -> {tag_disj} || {n}__d d")
    out.append(f"    | PList xs -> {n} xs")
    out.append("    | _ -> false end")
    out.append(f"  with {n}__d (d: pydict) : bool")
    out.append("    requires { true } ensures { true } variant { size_dict d }")
    out.append("  = match d with DNil -> false")
    out.append(f"    | DCons _ v rest -> {n}__v v || {n}__d rest end")
    return out


# =========================================================================
# A-bool LAST-ELEMENT tag-dispatch fold — `recognize_bool_lastelem`.
#
# A THIRD sibling source shape for the identical `emit_bool_multiway_group`
# catamorphism (no new WhyML): instead of folding over the WHOLE list
# (`recognize_bool_existence`) or a multiway dispatch inside a `for stmt in
# stmts` loop (`recognize_bool_multiway`), `ends_with_return`-shaped methods
# inspect only the LAST element:
#     if not <stmts>: return False
#     <last> = <stmts>[-1]
#     <st> = <last>.get("stmt") [or <last>.get("type")]
#     if <st> == "<TAG>": return True
#     if <st> == "<TAG2>": return (<self>(<last>.get("<k1>",[])) and/or
#                                   <self>(<last>.get("<k2>",[])))
#     ...
#     return False
# Under `ensures True` (insight C) the RETURN VALUE is unconstrained, so the
# recognizer does not need to reproduce "look only at the last element" —
# it only needs to certify the source IS this shape (fail-closed), then
# defers to the SAME whole-subtree OR-descend used for the other two bool
# shapes (`emit_bool_multiway_group`, reused verbatim via the identical
# {subject, tags} descriptor).
# =========================================================================


def _match_last_index_subscript(node: Any, subj: str) -> bool:
    """`<subj>[-1]` -- a Subscript whose index is the literal `-1`
    (`UnaryOp "-"` over `Number 1`, the IR shape for a negative literal)."""
    if not (isinstance(node, dict) and node.get("type") == "Subscript"
            and _is_var(node.get("value"), subj)):
        return False
    idx = node.get("index", {})
    return (isinstance(idx, dict) and idx.get("type") == "UnaryOp"
            and idx.get("op") == "-"
            and isinstance(idx.get("expr"), dict)
            and idx["expr"].get("type") == "Number"
            and idx["expr"].get("value") == 1)


def _match_last_tag_read(node: Any, lastv: str) -> bool:
    """`<lastv>.get("<key>")` alone, or `<lastv>.get("<k1>") or <lastv>.get(
    "<k2>")` -- the tag-discriminant read off the last element (`ends_with_
    return`-shaped: `last.get("stmt") or last.get("type")`). Either a single
    read or an `or`-fallback of two reads; fails closed otherwise."""
    if _match_get_call(node, lastv) is not None:
        return True
    if (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "or"):
        return (_match_get_call(node.get("left", {}), lastv) is not None
                and _match_get_call(node.get("right", {}), lastv) is not None)
    return False


def _match_bool_combo(node: Any, subjv: str, names: List[str]) -> bool:
    """Any `and`/`or` nesting of `_is_selfcall_like` leaves on `subjv`
    (`ends_with_return`-shaped: `self(last.get("body",[])) and self(last.get(
    "orelse",[]))`). Fails closed on anything else."""
    if (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") in ("and", "or")):
        return (_match_bool_combo(node.get("left", {}), subjv, names)
                and _match_bool_combo(node.get("right", {}), subjv, names))
    return _is_selfcall_like(node, subjv, names)


def _match_lastelem_arm_body(arm_body: List[Any], lastv: str,
                             names: List[str]) -> bool:
    """One last-element-dispatch arm's action: bare `return True`, or
    `return (<and/or-combo of self-calls into <lastv>'s body/orelse>)`."""
    if len(arm_body) != 1:
        return False
    if _is_bool_true_return(arm_body[0]):
        return True
    stmt = arm_body[0]
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Return"):
        return False
    return _match_bool_combo(stmt.get("value"), lastv, names)


def recognize_bool_lastelem(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the LAST-ELEMENT tag-dispatch A-bool statement-
    tree existence fold (`ends_with_return`-shaped). See the module comment
    above for the full shape. Returns {subject, tags} (the `emit_bool_
    multiway_group` descriptor, reused verbatim) or None. Never raises."""
    try:
        return _recognize_bool_lastelem(func)
    except Exception:
        return None


def _recognize_bool_lastelem(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    subj = params[0]
    pa = func.get("param_annotations", {})
    if pa.get(subj) != "list":
        return None
    if func.get("return_annotation") != "bool":
        return None
    body = func.get("body", [])
    if len(body) < 4:
        return None
    guard, bind, disc = body[0], body[1], body[2]
    rest = body[3:]
    # guard: if not <subj>: return False
    if not (isinstance(guard, dict) and guard.get("stmt") == "If"
            and not guard.get("orelse")):
        return None
    gtest = guard.get("test", {})
    if not (isinstance(gtest, dict) and gtest.get("type") == "UnaryOp"
            and gtest.get("op") == "not" and _is_var(gtest.get("expr"), subj)):
        return None
    gbody = guard.get("body", [])
    if not (len(gbody) == 1 and isinstance(gbody[0], dict)
            and gbody[0].get("stmt") == "Return"
            and isinstance(gbody[0].get("value"), dict)
            and gbody[0]["value"].get("type") == "Bool"
            and gbody[0]["value"].get("value") is False):
        return None
    # bind: <lastv> = <subj>[-1]
    if not (isinstance(bind, dict) and bind.get("stmt") == "Assign"
            and _match_last_index_subscript(bind.get("value", {}), subj)):
        return None
    lastv = bind.get("target")
    if not isinstance(lastv, str):
        return None
    # disc: <stv> = <lastv>.get("<key>") [or <lastv>.get("<key2>")]
    if not (isinstance(disc, dict) and disc.get("stmt") == "Assign"
            and _match_last_tag_read(disc.get("value", {}), lastv)):
        return None
    stv = disc.get("target")
    if not isinstance(stv, str):
        return None
    # rest: N tag-dispatch arms + a `return False` tail
    if len(rest) < 2:
        return None
    arms_stmts, tail = rest[:-1], rest[-1]
    if not (isinstance(tail, dict) and tail.get("stmt") == "Return"
            and isinstance(tail.get("value"), dict)
            and tail["value"].get("type") == "Bool"
            and tail["value"].get("value") is False):
        return None
    arms = _flatten_multiway_if_chain(arms_stmts)
    if not arms:
        return None
    names: List[str] = []
    tags: List[str] = []
    for test, arm_body in arms:
        arm_tags = _match_stype_tag_or_tags(test, stv)
        if not arm_tags:
            return None
        if not _match_lastelem_arm_body(arm_body, lastv, names):
            return None
        for t in arm_tags:
            if t not in tags:
                tags.append(t)
    if not names:
        return None
    return {"subject": subj, "tags": tags}


# =========================================================================
# A-bool ENUMERATE positional-dispatch fold — `recognize_bool_earlyreturn`.
#
# A FOURTH sibling source shape for the same `emit_bool_multiway_group`
# catamorphism: `has_early_return`-shaped methods loop `for i, stmt in
# enumerate(stmts)` (an index-tracking twin of `recognize_bool_multiway`'s
# plain `for stmt in stmts`) and thread the index into a POSITIONAL "is
# there a statement after this one" guard (`i < len(stmts) - 1`) that gates
# an otherwise-ordinary recursive-call arm. Under `ensures True` (insight C)
# the guard's VALUE is a fact the fold does not need — the recognizer only
# certifies the guard reads REAL accessors (the loop's own index var, `len`
# of the same list param), never evaluates it — then defers to the same
# whole-subtree OR-descend as every other bool-dispatch shape.
# =========================================================================


def _match_enumerate_for(node: Any, subj: str) -> Optional[tuple]:
    """`for <i>, <s> in enumerate(<subj>):` -> (idxvar, stmtvar), or None.
    Reads the IR's `tuple_targets` field (the front-end's enumerate/tuple-
    unpack target list) -- never inspects the loop body to find the names."""
    if not (isinstance(node, dict) and node.get("stmt") == "For"):
        return None
    it = node.get("iter", {})
    if not (isinstance(it, dict) and it.get("type") == "Call"
            and it.get("func") == "enumerate" and len(it.get("args", [])) == 1
            and _is_var(it["args"][0], subj)):
        return None
    tt = node.get("tuple_targets")
    if not (isinstance(tt, list) and len(tt) == 2
            and all(isinstance(x, str) for x in tt)):
        return None
    return tt[0], tt[1]


def _match_positional_guard(node: Any, idxvar: str, subj: str) -> bool:
    """`<idxvar> < len(<subj>) - <literal>` -- the positional "is there a
    statement after this one" guard (`has_early_return`-shaped). Structural
    only: under `ensures True` the guard's VALUE is unneeded (insight C), so
    this validates the guard's SHAPE (the same index var bound by the
    enclosing `enumerate` loop, `len` of the same list param) without
    evaluating the comparison."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "<" and _is_var(node.get("left"), idxvar)):
        return False
    right = node.get("right", {})
    if not (isinstance(right, dict) and right.get("type") == "BinOp"
            and right.get("op") == "-"):
        return False
    lenc = right.get("left", {})
    if not (isinstance(lenc, dict) and lenc.get("type") == "Call"
            and lenc.get("func") == "len" and len(lenc.get("args", [])) == 1
            and _is_var(lenc["args"][0], subj)):
        return False
    lit = right.get("right", {})
    return isinstance(lit, dict) and lit.get("type") == "Number"


def _match_guarded_call_return(stmts_slice: List[Any], stmtv: str, idxvar: str,
                               subj: str, names: List[str]) -> int:
    """3-statement `<retv> = <call>(<stmtv>...); <restv> = <positional-
    guard>; if <retv> and <restv>: return True` arm-prefix (`has_early_
    return`-shaped): a genuine self/sibling call bound to a local, ANDed
    with a positional "trailing statement" fact (dropped under `ensures
    True` -- insight C), gating a bare `return True`. Returns 3 (consumed)
    or 0 (no match)."""
    if len(stmts_slice) < 3:
        return 0
    a0, a1, a2 = stmts_slice[0], stmts_slice[1], stmts_slice[2]
    if not (isinstance(a0, dict) and a0.get("stmt") == "Assign"):
        return 0
    retv = a0.get("target")
    if not (isinstance(retv, str) and _is_selfcall_like(a0.get("value", {}), stmtv, names)):
        return 0
    if not (isinstance(a1, dict) and a1.get("stmt") == "Assign"):
        return 0
    restv = a1.get("target")
    if not (isinstance(restv, str)
            and _match_positional_guard(a1.get("value", {}), idxvar, subj)):
        return 0
    if not (isinstance(a2, dict) and a2.get("stmt") == "If" and not a2.get("orelse")):
        return 0
    test = a2.get("test", {})
    if not (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "and" and _is_var(test.get("left"), retv)
            and _is_var(test.get("right"), restv)):
        return 0
    if not (len(a2.get("body", [])) == 1 and _is_bool_true_return(a2["body"][0])):
        return 0
    return 3


def _match_earlyreturn_if_arm(arm_body: List[Any], stmtv: str, idxvar: str,
                              subj: str, names: List[str]) -> bool:
    """The `has_early_return`-shaped If-tag arm: the 3-statement guarded-
    call-return prefix, followed by 1-2 trailing `if <call>(<stmtv>...):
    return True` self-descend arms."""
    consumed = _match_guarded_call_return(arm_body, stmtv, idxvar, subj, names)
    if not consumed:
        return False
    trailing = arm_body[consumed:]
    if not (1 <= len(trailing) <= 2):
        return False
    for s in trailing:
        if not (isinstance(s, dict) and s.get("stmt") == "If" and not s.get("orelse")
                and _is_selfcall_like(s.get("test", {}), stmtv, names)
                and len(s.get("body", [])) == 1 and _is_bool_true_return(s["body"][0])):
            return False
    return True


def _match_earlyreturn_try_arm(arm_body: List[Any], stmtv: str, idxvar: str,
                               subj: str, names: List[str]) -> bool:
    """The `has_early_return`-shaped Try-tag arm: `<hvarlist> = <stmtv>.get(
    "handlers", []); for <h> in <hvarlist>: (if <call>(<h>...): if
    <positional-guard>: return True); (if <call>(<h>...): return True); if
    <call>(<stmtv>...): return True` -- a handlers-loop-FIRST reordering of
    `_match_try_handlers_arm` with a positional-gated inner arm."""
    if len(arm_body) != 3:
        return False
    s0, s1, s2 = arm_body
    if not (isinstance(s0, dict) and s0.get("stmt") == "Assign"
            and _match_get_call(s0.get("value", {}), stmtv) == "handlers"):
        return False
    hvar_list = s0.get("target")
    if not isinstance(hvar_list, str):
        return False
    if not (isinstance(s1, dict) and s1.get("stmt") == "For"
            and _is_var(s1.get("iter"), hvar_list)):
        return False
    hvar = s1.get("target")
    if not isinstance(hvar, str):
        return False
    lb = s1.get("body", [])
    if len(lb) != 2:
        return False
    i0, i1 = lb
    if not (isinstance(i0, dict) and i0.get("stmt") == "If" and not i0.get("orelse")
            and _is_selfcall_like(i0.get("test", {}), hvar, names)):
        return False
    ib = i0.get("body", [])
    if not (len(ib) == 1 and isinstance(ib[0], dict) and ib[0].get("stmt") == "If"
            and not ib[0].get("orelse")
            and _match_positional_guard(ib[0].get("test", {}), idxvar, subj)
            and len(ib[0].get("body", [])) == 1 and _is_bool_true_return(ib[0]["body"][0])):
        return False
    if not (isinstance(i1, dict) and i1.get("stmt") == "If" and not i1.get("orelse")
            and _is_selfcall_like(i1.get("test", {}), hvar, names)
            and len(i1.get("body", [])) == 1 and _is_bool_true_return(i1["body"][0])):
        return False
    return (isinstance(s2, dict) and s2.get("stmt") == "If" and not s2.get("orelse")
            and _is_selfcall_like(s2.get("test", {}), stmtv, names)
            and len(s2.get("body", [])) == 1 and _is_bool_true_return(s2["body"][0]))


def recognize_bool_earlyreturn(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the ENUMERATE positional-dispatch A-bool
    statement-tree existence fold (`has_early_return`-shaped). See the
    module comment above. Returns {subject, tags} (the `emit_bool_multiway_
    group` descriptor, reused verbatim) or None. Never raises."""
    try:
        return _recognize_bool_earlyreturn(func)
    except Exception:
        return None


def _recognize_bool_earlyreturn(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    subj = params[0]
    pa = func.get("param_annotations", {})
    if pa.get(subj) != "list":
        return None
    if func.get("return_annotation") != "bool":
        return None
    body = func.get("body", [])
    if len(body) != 2:
        return None
    loop, tail = body
    if not (isinstance(tail, dict) and tail.get("stmt") == "Return"
            and isinstance(tail.get("value"), dict)
            and tail["value"].get("type") == "Bool"
            and tail["value"].get("value") is False):
        return None
    idx_stmt = _match_enumerate_for(loop, subj)
    if idx_stmt is None:
        return None
    idxvar, stmtv = idx_stmt
    lbody = loop.get("body", [])
    if len(lbody) < 2:
        return None
    a0 = lbody[0]
    if not (isinstance(a0, dict) and a0.get("stmt") == "Assign"
            and _match_get_call(a0.get("value", {}), stmtv) == "stmt"):
        return None
    stypev = a0.get("target")
    if not isinstance(stypev, str):
        return None
    arms = _flatten_multiway_if_chain(lbody[1:])
    if not arms:
        return None
    names: List[str] = []
    tags: List[str] = []
    for test, arm_body in arms:
        arm_tags = _match_stype_tag_or_tags(test, stypev)
        if not arm_tags:
            return None
        ok = (_match_multiway_arm_body(arm_body, stmtv, names)
              or _match_earlyreturn_if_arm(arm_body, stmtv, idxvar, subj, names)
              or _match_earlyreturn_try_arm(arm_body, stmtv, idxvar, subj, names))
        if not ok:
            return None
        for t in arm_tags:
            if t not in tags:
                tags.append(t)
    if not names:
        return None
    return {"subject": subj, "tags": tags}


# =========================================================================
# bigger-build G-set-accumulate-multiway — the Set[str] statement-tree
# accumulate fold: the BY-RETURN sibling of `recognize_bool_existence`
# (same `list pyval`/tag-dispatch/body-orelse-descend statement-tree shape)
# whose result algebra is a returned `Set[str]` (the `recognize_setfold`
# `map string bool` algebra) instead of `bool`. Reuses BOTH existing
# machineries verbatim — no new WhyML theory, no new abstract op, no axiom:
# the `pyval`/`pydict`/`size*` L1 theory (`needs_pydict`) and the purely-
# defined `set_add`/`set_union` (`map string bool`) already certified by
# `recognize_setfold`.
#
# Recognized shape (`find_lambda_vars`/`find_record_vars`):
#     <acc> = set()
#     for <stmt> in <stmts>:
#         if <stmt>.get("stmt") == "<TAG>":              # optional add-arm
#             <val> = <stmt>.get("value", {})
#             if isinstance(<val>, dict) and <guards on val>:
#                 <acc>.add(<stmt>.get("<addkey>", ""))
#         for key in ("body", "orelse"):                  # required descend
#             if key in <stmt> [and isinstance(<stmt>[key], list)]:
#                 <acc> |= self(<stmt>[key][, extra...])
#         if <stmt>.get("stmt") == "While": <acc> |= self(<stmt>.get("body", [])[, extra...])   # optional echo
#         if <stmt>.get("stmt") == "For": <acc> |= self(<stmt>.get("body", [])[, extra...])      # optional echo
#         if <stmt>.get("stmt") == "Match":                                                       # optional echo
#             for c in <stmt>.get("cases", []): <acc> |= self(c.get("body", [])[, extra...])
#     return <acc>
#
# Under `ensures True` (insight C, `recognize_bool_existence`'s doctrine) the
# WhyML lowering does NOT need to replicate the selective body/orelse/cases
# projection: the emitted catamorphism OR-unions (via `set_add`) the whole
# `pydict` subtree (the proven `emit_bool_existence_group`/`emit_setfold_group`
# walk), a superset of the Python recursion — the redundant While/For/Match
# echo arms are then no-ops under the returned-value-unconstrained contract,
# so the recognizer only needs to VALIDATE their presence (fail-closed: any
# other trailing arm rejects), never re-derive their (redundant) contribution.
# =========================================================================


def _match_field_eq_guard(node: Any, valv: str) -> Optional[tuple]:
    """`<valv>.get("<key>"[, default]) == "<lit>"` -> (key, lit) or None."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp" and node.get("op") == "=="):
        return None
    key = _match_get_call(node.get("left", {}), valv)
    if key is None:
        return None
    lit = _is_string(node.get("right"))
    if lit is None:
        return None
    return (key, lit)


def _match_field_in_guard(node: Any, valv: str, extra: List[str]) -> Optional[tuple]:
    """`<valv>.get("<key>"[, default]) in <extra_set_param>` -> (key, param) or
    None. The right operand must be one of the threaded `set`-typed params."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp" and node.get("op") == "in"):
        return None
    key = _match_get_call(node.get("left", {}), valv)
    if key is None:
        return None
    right = node.get("right", {})
    if not (_is_var(right) and right.get("name") in extra):
        return None
    return (key, right.get("name"))


def _match_self_pred_guard(node: Any, valv: str) -> Optional[str]:
    """`self.<pred>(<valv>)` — an instance-method BOOLEAN guard over the
    isinstance-narrowed value local (`self._rhs_yields_map(val)`). Returns the
    predicate method tail (e.g. `"_rhs_yields_map"`) or None. The predicate is
    modelled as an OPAQUE trusted bool over the value pyval — a legitimate
    opaque-reader boundary (like `symtab_mem`/`csl_mutex_ast`), NOT an axiom —
    so only the SHAPE (a self-method applied to exactly the narrowed local) is
    validated, fail-closed. A sibling call with an extra arg, a non-`self`
    receiver, or a different argument rejects."""
    if not (isinstance(node, dict) and node.get("type") == "Call"):
        return None
    f = node.get("func")
    if not isinstance(f, str) or not f.startswith("self."):
        return None
    args = node.get("args", [])
    if len(args) != 1 or not _is_var(args[0], valv):
        return None
    meth = f[len("self."):]
    return meth or None


def _pred_whyml_name(n: str, meth: str) -> str:
    """WhyML-safe opaque-predicate name for a `self.<meth>` guard, per method
    group `n` (so distinct methods never collide)."""
    return f"{n}__pred_" + "".join(c if c.isalnum() else "_" for c in meth)


def _match_direct_add_expr(stmt: Any, acc: str, stmtv: str) -> Optional[str]:
    """`<acc>.add(<stmtv>.get("<key>"[, default]))` as an ExprStmt -> key."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Expr"):
        return None
    call = stmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add" and len(call.get("args", [])) == 1):
        return None
    return _match_get_call(call["args"][0], stmtv)


def _match_stmt_arm_add_body(ibody: List[Any], stmtv: str, acc: str) -> Optional[str]:
    """The add-arm inner body -> the literal add-key, for EITHER:
      * direct    `[<acc>.add(<stmtv>.get("<key>"))]` (len 1), OR
      * indirect  `[<tgt> = <stmtv>.get("<key>"[, def]); if <tgt>: <acc>.add(<tgt>)]`
        (len 2) — a bind + truthiness-guard + add-of-local. Under `ensures True`
        the `if <tgt>:` truthiness guard is subsumed by the emission's
        `option`-match (an absent/empty key reads `None` -> `const false`
        regardless), so only the SHAPE is validated and the bound local's
        literal-key PROVENANCE (`<stmtv>.get("<key>")`) becomes the emitted add
        source. Fail-closed."""
    if len(ibody) == 1:
        return _match_direct_add_expr(ibody[0], acc, stmtv)
    if len(ibody) == 2:
        asg, addif = ibody
        if not (isinstance(asg, dict) and asg.get("stmt") == "Assign"):
            return None
        tgt = asg.get("target")
        if not isinstance(tgt, str):
            return None
        key = _match_get_call(asg.get("value", {}), stmtv)
        if key is None:
            return None
        if not (isinstance(addif, dict) and addif.get("stmt") == "If"
                and not addif.get("orelse") and _is_var(addif.get("test"), tgt)):
            return None
        ab = addif.get("body", [])
        if len(ab) != 1:
            return None
        a0 = ab[0]
        if not (isinstance(a0, dict) and a0.get("stmt") == "Expr"):
            return None
        cv = a0.get("value", {})
        if not (isinstance(cv, dict) and cv.get("type") == "Call"
                and cv.get("func") == f"{acc}.add" and len(cv.get("args", [])) == 1
                and _is_var(cv["args"][0], tgt)):
            return None
        return key
    return None


def _match_stmt_add_arm(stmt: Any, stmtv: str, acc: str,
                        extra: List[str]) -> Optional[Dict[str, Any]]:
    """Optional add-arm:
        if <stmt>.get("stmt") == "<TAG>":
            <val> = <stmt>.get("value", {})
            if isinstance(<val>, dict) and <guards>:
                <acc>.add(<stmt>.get("<addkey>"[, default]))
    `<guards>` is a conjunction of one-or-more `<val>.get(k)==lit` (eq) /
    `<val>.get(k) in <extra_set_param>` (in) tests, AND/OR an opaque
    self-predicate `self.<pred>(<val>)` (`pred_guarded`, see
    `_match_self_pred_guard`), in any mix. The add body is the direct
    `<acc>.add(<stmt>.get(...))` OR the indirect
    `<tgt> = <stmt>.get(...); if <tgt>: <acc>.add(<tgt>)` shape
    (`_match_stmt_arm_add_body`). Returns
    {outer_tag, val_local, guards: [(kind, key, lit_or_param)], add_key,
    preds?: [meth]} or None (fail-closed)."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "If":
        return None
    if stmt.get("orelse"):
        return None
    outer_tag = _match_stmt_tag_test(stmt.get("test", {}), stmtv)
    if outer_tag is None:
        return None
    body = stmt.get("body", [])
    if len(body) != 2:
        return None
    asg = body[0]
    if not (isinstance(asg, dict) and asg.get("stmt") == "Assign"):
        return None
    valv = asg.get("target")
    if not isinstance(valv, str):
        return None
    if _match_get_call(asg.get("value", {}), stmtv) != "value":
        return None
    inner = body[1]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If" and not inner.get("orelse")):
        return None
    conjuncts = _flatten_and(inner.get("test", {}))
    saw_isinstance = False
    guards: List[tuple] = []
    preds: List[str] = []
    for c in conjuncts:
        if (isinstance(c, dict) and c.get("type") == "Call" and c.get("func") == "isinstance"
                and len(c.get("args", [])) == 2 and _is_var(c["args"][0], valv)
                and _is_var(c["args"][1], "dict")):
            if saw_isinstance:
                return None
            saw_isinstance = True
            continue
        eq = _match_field_eq_guard(c, valv)
        if eq is not None:
            guards.append(("eq", eq[0], eq[1]))
            continue
        mem = _match_field_in_guard(c, valv, extra)
        if mem is not None:
            guards.append(("in", mem[0], mem[1]))
            continue
        pred = _match_self_pred_guard(c, valv)
        if pred is not None:
            preds.append(pred)
            continue
        return None
    if not saw_isinstance or not (guards or preds):
        return None
    add_key = _match_stmt_arm_add_body(inner.get("body", []), stmtv, acc)
    if add_key is None:
        return None
    desc = {"kind": "value_guarded", "outer_tag": outer_tag, "val_local": valv,
            "guards": guards, "add_key": add_key}
    if preds:
        desc["preds"] = preds
    return desc


# ---- G-set-accumulate-simple: the CHAIN add-arm (`find_append_targets`) -----
#
# A second add-arm shape: instead of ONE nested value+isinstance+guards level
# (`_match_stmt_add_arm`), the guard is a CHAIN of N literal-key `.get()`
# projections, each re-bound to a fresh local and re-guarded (a field-equality
# OR a string-method boolean test, e.g. `.endswith(".append")`), terminating
# in `<acc>.add(<EXPR>)` where `<EXPR>` may be an arbitrary value TRANSFORM
# (`.rsplit(...)[0].replace(...)`) of one of the chain's bound locals — under
# `ensures True` (insight C, the doctrine this whole module applies
# throughout: substmap's scope-cut note, `_match_pre_action_nested_field`'s
# guard-narrowing, `_match_set_pre_action_tuple`'s `local_read` kind) the
# EXACT string added is a value fact the certified contract does not need, so
# the transform is DROPPED and the chain's OWN literal-key projection (the
# local's PROVENANCE, traced back through the transform) becomes the emitted
# add source. Reuses the identical per-key `pydict` readers and `set_add`
# machinery as every other shape in this family — no new WhyML theory.

_STR_BOOL_METHODS = {"endswith", "startswith"}


def _match_method_bool_guard(node: Any, local: str) -> bool:
    """`<local>.<endswith|startswith>("<lit>")` — a string-method boolean
    guard. The literal argument and the boolean result are both value facts
    `ensures True` does not need; only the SHAPE (which local it tests) is
    validated, fail-closed."""
    if not (isinstance(node, dict) and node.get("type") == "Call"):
        return False
    f = node.get("func")
    if not isinstance(f, str) or "." not in f:
        return False
    recv, meth = f.rsplit(".", 1)
    if recv != local or meth not in _STR_BOOL_METHODS:
        return False
    args = node.get("args", [])
    return len(args) == 1 and _is_string(args[0]) is not None


def _match_field_bind(stmt: Any) -> Optional[tuple]:
    """`<name> = <parent>.get("<key>"[, default])` -> (name, parent, key) or
    None. `<parent>` is a dotted-call receiver (a string PREFIX of the `func`
    attribute, e.g. `"val.get"` -> receiver `"val"`), not a Var argument."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Assign"):
        return None
    name = stmt.get("target")
    if not isinstance(name, str):
        return None
    val = stmt.get("value", {})
    if not (isinstance(val, dict) and val.get("type") == "Call"):
        return None
    f = val.get("func")
    if not isinstance(f, str) or not f.endswith(".get"):
        return None
    parent = f[:-len(".get")]
    args = val.get("args", [])
    if not args:
        return None
    key = _is_string(args[0])
    if key is None:
        return None
    return (name, parent, key)


def _collect_refs(node: Any, out: set) -> None:
    """Recursively collect every Var name AND every dotted-call RECEIVER name
    referenced anywhere in `node` (an arbitrary expression IR subtree). A
    dotted-call receiver (e.g. `func` in `func.rsplit(...)`) is encoded as a
    string PREFIX of the `func` attribute, not a separate Var node, so it
    needs its own extraction alongside the plain Var case."""
    if isinstance(node, dict):
        if node.get("type") == "Var" and isinstance(node.get("name"), str):
            out.add(node["name"])
        f = node.get("func")
        if isinstance(f, str) and "." in f:
            out.add(f.rsplit(".", 1)[0])
        for v in node.values():
            _collect_refs(v, out)
    elif isinstance(node, list):
        for x in node:
            _collect_refs(x, out)


def _refs_single_root(expr: Any, paths: Dict[str, List[str]],
                      stmtv: str) -> Optional[List[str]]:
    """Trace `expr` (a value TRANSFORM, e.g. `arr_name.replace(".", "_")`)
    back to the SINGLE chain-bound local (or `stmtv` itself) it is built
    from — every Var/receiver referenced in `expr` must resolve to the SAME
    field-path, else ambiguous (fail-closed). Returns that field path (the
    ordered list of literal keys from `stmtv`), or None."""
    names: set = set()
    _collect_refs(expr, names)
    resolved: set = set()
    for nm in names:
        if nm == stmtv:
            resolved.add(())
        elif nm in paths:
            resolved.add(tuple(paths[nm]))
        else:
            return None
    if len(resolved) != 1:
        return None
    return list(next(iter(resolved)))


def _match_chain_add_arm(stmt: Any, stmtv: str, acc: str) -> Optional[Dict[str, Any]]:
    """CHAIN add-arm (`find_append_targets` shape):
        if <stmt-tag-test>:
            <l1> = <stmtv-or-local>.get("<k1>"[, default])
            if <field-eq guard on l1> | <method-bool guard on l1>:
                <l2> = <l1>.get("<k2>"[, default])
                if <guard on l2>:
                    ...
                    [<transform> = <expr over ONE bound local>]   # optional
                    <acc>.add(<expr over ONE bound local>)
    Returns {kind: "chain", outer_tag, field_path: [k1, k2, ...]} — the
    literal-key projection chain from `stmtv` down to the local whose
    PROVENANCE the (possibly transformed) add argument traces to — or None
    (fail-closed)."""
    if not isinstance(stmt, dict) or stmt.get("stmt") != "If":
        return None
    if stmt.get("orelse"):
        return None
    outer_tag = _match_stmt_tag_test(stmt.get("test", {}), stmtv)
    if outer_tag is None:
        return None
    paths: Dict[str, List[str]] = {}
    cur = stmt.get("body", [])
    while len(cur) == 2:
        bind = _match_field_bind(cur[0])
        guardif = cur[1]
        if bind is None or not (isinstance(guardif, dict) and guardif.get("stmt") == "If"
                                and not guardif.get("orelse")):
            break
        name, parent, key = bind
        if parent == stmtv:
            base: List[str] = []
        elif parent in paths:
            base = paths[parent]
        else:
            return None
        guard = guardif.get("test", {})
        if not (_match_field_eq_guard(guard, name) is not None
                or _match_method_bool_guard(guard, name)):
            return None
        paths[name] = base + [key]
        cur = guardif.get("body", [])
    # terminal body: an OPTIONAL single transform-Assign, then the add call.
    idx = 0
    if len(cur) >= 1 and isinstance(cur[0], dict) and cur[0].get("stmt") == "Assign":
        tname = cur[0].get("target")
        troot = _refs_single_root(cur[0].get("value"), paths, stmtv)
        if isinstance(tname, str) and troot is not None:
            paths[tname] = troot
            idx = 1
    if len(cur) != idx + 1:
        return None
    addstmt = cur[idx]
    if not (isinstance(addstmt, dict) and addstmt.get("stmt") == "Expr"):
        return None
    call = addstmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add" and len(call.get("args", [])) == 1):
        return None
    add_path = _refs_single_root(call["args"][0], paths, stmtv)
    if not add_path:
        return None
    return {"kind": "chain", "outer_tag": outer_tag, "field_path": add_path}


# ---- G-set-accumulate-elif-chain (`find_ghost_vars`) ------------------------
#
# A third loop-body shape: instead of an optional add-arm followed by an
# UNCONDITIONAL descend-loop over `("body", "orelse")` (the shape above), the
# ENTIRE loop body is a single right-leaning If/orelse ELIF CHAIN — one tag
# per leaf, EXACTLY ONE leaf is the add-arm (`<acc>.add(<field-ref>)`, a
# direct Subscript/`.get()` projection, no value-nesting), every OTHER leaf is
# a descend-arm (1+ self-recursive union statements), and unmatched tags fall
# through a terminal empty `orelse` (a no-op). Both syntactic union forms
# Python offers are accepted: `<acc> |= <self>(...)` (AugAssign) AND
# `<acc>.update(<self>(...))` (a method-call ExprStmt) — `set.update(x)` and
# `set |= x` are semantically identical, so both lower to the same
# `set_union`. Under `ensures True` the emitted full-subtree OR-union
# catamorphism (identical to the shape above) is a sound SUPERSET of
# whichever fields each leaf selectively recurses into, so the descend
# leaves are only VALIDATED (fail-closed shape check), never individually
# replayed — no new WhyML theory, the SAME `n__d`/`n__v` walk emits both
# shapes.

def _match_field_ref(node: Any, subj: str) -> Optional[str]:
    """`<subj>[<lit>]` (Subscript) or `<subj>.get(<lit>[, default])` (Call) ->
    the literal key, else None. Both syntactic forms project the same field."""
    key = _match_subscript_str(node, subj)
    if key is not None:
        return key
    return _match_get_call(node, subj)


def _match_elif_union_stmt(stmt: Any, stmtv: str, acc: str, fname: str,
                           extra: List[str]) -> bool:
    """`<acc> |= <self>(<field-ref>[, extra...])` OR
    `<acc>.update(<self>(<field-ref>[, extra...]))` — the two syntactic forms
    Python offers for set union-accumulation; both are accepted (same
    `set_union` semantics)."""
    call = None
    if (isinstance(stmt, dict) and stmt.get("stmt") == "AugAssign"
            and stmt.get("target") == acc and stmt.get("op") == "|"):
        call = stmt.get("value", {})
    elif isinstance(stmt, dict) and stmt.get("stmt") == "Expr":
        v = stmt.get("value", {})
        if (isinstance(v, dict) and v.get("type") == "Call"
                and v.get("func") == f"{acc}.update" and len(v.get("args", [])) == 1):
            call = v["args"][0]
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return False
    cf = call.get("func")
    if not isinstance(cf, str) or _canon_call(cf) != fname:
        return False
    args = call.get("args", [])
    if len(args) != 1 + len(extra):
        return False
    if not all(_is_var(args[1 + i], e) for i, e in enumerate(extra)):
        return False
    return _match_field_ref(args[0], stmtv) is not None


def _match_elif_add_body(body: Any, stmtv: str, acc: str) -> Optional[str]:
    """A leaf's body is exactly `<acc>.add(<field-ref-on-stmt>)`."""
    if not (isinstance(body, list) and len(body) == 1):
        return None
    st0 = body[0]
    if not (isinstance(st0, dict) and st0.get("stmt") == "Expr"):
        return None
    call = st0.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add" and len(call.get("args", [])) == 1):
        return None
    return _match_field_ref(call["args"][0], stmtv)


def _match_elif_descend_body(body: Any, stmtv: str, acc: str, fname: str,
                             extra: List[str]) -> bool:
    """A leaf's body is 1+ self-recursive union statements (any mix of the
    two syntactic forms), and nothing else."""
    return bool(body) and all(_match_elif_union_stmt(st, stmtv, acc, fname, extra)
                              for st in body)


def _match_elif_chain(node: Any, stmtv: str, acc: str, fname: str,
                      extra: List[str]) -> Optional[Dict[str, Any]]:
    """Parse a right-leaning If/orelse elif-chain. Exactly ONE leaf is the
    add-arm; every other leaf is a descend-arm; every tag is distinct; the
    chain must terminate in an empty `orelse` (fail-closed — no unrecognized
    tail action). Returns {kind: "direct", outer_tag, add_key} or None."""
    add: Optional[tuple] = None
    seen_tags: set = set()
    cur = node
    while True:
        if not (isinstance(cur, dict) and cur.get("stmt") == "If"):
            return None
        tag = _match_stmt_tag_test(cur.get("test", {}), stmtv)
        if tag is None or tag in seen_tags:
            return None
        seen_tags.add(tag)
        body = cur.get("body", [])
        add_key = _match_elif_add_body(body, stmtv, acc)
        if add_key is not None:
            if add is not None:
                return None
            add = (tag, add_key)
        elif not _match_elif_descend_body(body, stmtv, acc, fname, extra):
            return None
        orelse = cur.get("orelse", [])
        if not orelse:
            break
        if len(orelse) != 1:
            return None
        cur = orelse[0]
    if add is None:
        return None
    return {"kind": "direct", "outer_tag": add[0], "add_key": add[1]}


def _match_stmt_union_call(node: Any, acc: str, fname: str, extra: List[str]) -> Optional[List[Any]]:
    """`<self>(<arg0>[, extra...])` as a Call value -> its args list, or None
    (does not check `arg0`'s own shape — the caller does). `<self>` resolves to
    this same function via `_call_is_self`: the module-level bare name, the
    class-qualified static call, OR the instance-method `self.<meth>`
    self-recursion (the emitted name is `<class>__<meth>`). The `self.` arm lets
    an INSTANCE-method stmt-fold (`_collect_dict_var_assigns`) match, where the
    prior bare-`_canon_call` equality only covered `@staticmethod` folds."""
    if not (isinstance(node, dict) and node.get("type") == "Call"):
        return None
    cf = node.get("func")
    if not isinstance(cf, str) or not _call_is_self(cf, fname):
        return None
    args = node.get("args", [])
    if len(args) != 1 + len(extra):
        return None
    if not all(_is_var(args[1 + i], e) for i, e in enumerate(extra)):
        return None
    return args


def _match_stmt_descend_loop(node: Any, stmtv: str, acc: str, fname: str,
                             extra: List[str]) -> bool:
    """Required descend-arm:
        for key in ("body", "orelse"):
            if key in <stmt> [and isinstance(<stmt>[key], list)]:
                <acc> |= self(<stmt>[key][, extra...])"""
    if not (isinstance(node, dict) and node.get("stmt") == "For"):
        return False
    it = node.get("iter", {})
    if not (isinstance(it, dict) and it.get("type") == "Tuple"):
        return False
    if [_is_string(e) for e in it.get("elts", [])] != ["body", "orelse"]:
        return False
    keyv = node.get("target")
    lb = node.get("body", [])
    if len(lb) != 1:
        return False
    iff = lb[0]
    if not (isinstance(iff, dict) and iff.get("stmt") == "If" and not iff.get("orelse")):
        return False
    conjuncts = _flatten_and(iff.get("test", {}))
    c0 = conjuncts[0]
    if not (isinstance(c0, dict) and c0.get("type") == "BinOp" and c0.get("op") == "in"
            and _is_var(c0.get("left"), keyv) and _is_var(c0.get("right"), stmtv)):
        return False
    if len(conjuncts) == 2:
        c1 = conjuncts[1]
        if not (isinstance(c1, dict) and c1.get("type") == "Call" and c1.get("func") == "isinstance"
                and len(c1.get("args", [])) == 2 and _is_var(c1["args"][1], "list")):
            return False
        sub = c1["args"][0]
        if not (isinstance(sub, dict) and sub.get("type") == "Subscript"
                and _is_var(sub.get("value"), stmtv) and _is_var(sub.get("index"), keyv)):
            return False
    elif len(conjuncts) != 1:
        return False
    body = iff.get("body", [])
    if len(body) != 1:
        return False
    aug = body[0]
    if not (isinstance(aug, dict) and aug.get("stmt") == "AugAssign"
            and aug.get("target") == acc and aug.get("op") == "|"):
        return False
    args = _match_stmt_union_call(aug.get("value", {}), acc, fname, extra)
    if args is None:
        return False
    arg0 = args[0]
    return (isinstance(arg0, dict) and arg0.get("type") == "Subscript"
            and _is_var(arg0.get("value"), stmtv) and _is_var(arg0.get("index"), keyv))


def _match_union_rec_field(stmt0: Any, acc: str, fname: str, extra: List[str],
                           srcvar: str, key: str) -> bool:
    """`<acc> |= self(<srcvar>.get("<key>"[, default])[, extra...])`."""
    if not (isinstance(stmt0, dict) and stmt0.get("stmt") == "AugAssign"
            and stmt0.get("target") == acc and stmt0.get("op") == "|"):
        return False
    args = _match_stmt_union_call(stmt0.get("value", {}), acc, fname, extra)
    if args is None:
        return False
    return _match_get_call(args[0], srcvar) == key


def _match_echo_arm(stmt: Any, stmtv: str, acc: str, fname: str,
                    extra: List[str]) -> Optional[str]:
    """Optional REDUNDANT (under `ensures True`) echo-arm — recognized so the
    matcher fail-closes on anything ELSE trailing the loop, never to re-derive
    its (already-covered-by-the-full-subtree-walk) contribution:
        if <stmt>.get("stmt") == "While": <acc> |= self(<stmt>.get("body", [])[, extra...])
        if <stmt>.get("stmt") == "For": <acc> |= self(<stmt>.get("body", [])[, extra...])
        if <stmt>.get("stmt") == "Match":
            for c in <stmt>.get("cases", []): <acc> |= self(c.get("body", [])[, extra...])
        if <stmt>.get("stmt") == "Try":
            for h in <stmt>.get("handlers", []): <acc> |= self(h.get("body", [])[, extra...])
    Returns the matched tag or None. The `Try`/handlers walk is redundant with
    the general full-subtree `n__d`/`n__v` OR-walk (which already descends into
    the `handlers` list and each handler's `body`), so it is validated as SHAPE
    ONLY and contributes nothing to emission — exactly like the `Match`/cases
    arm."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "If" and not stmt.get("orelse")):
        return None
    tag = _match_stmt_tag_test(stmt.get("test", {}), stmtv)
    if tag is None:
        return None
    body = stmt.get("body", [])
    if tag in ("Match", "Try"):
        elem_key = "cases" if tag == "Match" else "handlers"
        if len(body) != 1:
            return None
        loop = body[0]
        if not (isinstance(loop, dict) and loop.get("stmt") == "For"):
            return None
        if _match_get_call(loop.get("iter", {}), stmtv) != elem_key:
            return None
        cvar = loop.get("target")
        lb = loop.get("body", [])
        if not isinstance(cvar, str) or len(lb) != 1:
            return None
        return tag if _match_union_rec_field(lb[0], acc, fname, extra, cvar, "body") else None
    if len(body) != 1:
        return None
    return tag if _match_union_rec_field(body[0], acc, fname, extra, stmtv, "body") else None


# ---- G-set-accumulate-trywalk (`collect_user_exceptions`) -------------------
#
# A fourth loop-body shape: after the optional simple add-arm, an OPTIONAL
# additional arm gated on a distinct tag whose body is `for <h> in
# <stmtv>.get("<key>", []): <exc-split-add chain>; <acc> |= self(<h>.get("<key2>",
# [])[, extra...])` — i.e. a nested per-element walk (over e.g. a `Try`'s
# `handlers` list) that both (a) ADDS a value derived from a nested field
# (`h.get("exc_type")`, split/stripped into pieces) and (b) self-recurses into
# a nested field of each element (`h.get("body")`). Under `ensures True`
# neither needs separate emission: (a) is a value fact the certified contract
# does not need (same scope-cut doctrine as the chain add-arm's dropped
# transform — insight C), and (b) is already a SOUND SUPERSET of what the
# standard full-subtree `n__d`/`n__v` OR-walk covers (it descends into EVERY
# dict field, including a nested list-of-dicts under an arbitrary key, so the
# handler-body recursion is redundant with the general walk exactly like an
# echo-arm's contribution). So this arm is validated as SHAPE ONLY
# (fail-closed) and contributes NOTHING to `emit_stmt_setfold_group` beyond
# what the existing `direct`/`chain`/`value_guarded` pre-action (from the
# arm ahead of it) already emits — no new WhyML theory, no new pre_action
# kind, no new reader.

def _match_stmt_direct_add_arm(stmt: Any, stmtv: str, acc: str) -> Optional[Dict[str, Any]]:
    """Simple compound-guarded add-arm (`collect_user_exceptions`'s first
    arm):
        if <stmtv>.get("stmt") == "<TAG>" and <stmtv>.get("<key>"):
            <acc>.add(<field-ref-on-stmt>)
    (Subscript or `.get()` field-ref, either syntactic form.) The truthy
    second conjunct is a value fact already subsumed by the `direct`
    emission's `option`-match (an absent/falsy key reads `None` -> `const
    false` regardless), so only the SHAPE — including that the truthy-tested
    key equals the add source — is validated. Returns {kind: "direct",
    outer_tag, add_key} or None (fail-closed)."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "If" and not stmt.get("orelse")):
        return None
    conjuncts = _flatten_and(stmt.get("test", {}))
    if len(conjuncts) != 2:
        return None
    tag = _match_stmt_tag_test(conjuncts[0], stmtv)
    if tag is None:
        return None
    truthy_key = _match_field_ref(conjuncts[1], stmtv)
    if truthy_key is None:
        return None
    add_key = _match_elif_add_body(stmt.get("body", []), stmtv, acc)
    if add_key is None or add_key != truthy_key:
        return None
    return {"kind": "direct", "outer_tag": tag, "add_key": add_key}


def _match_trywalk_exc_block(assign: Any, ifblock: Any, hvar: str, acc: str) -> bool:
    """`<v> = <hvar>.get("<key>"); if <v>: for <ep> in <v>.split("<sep>"):
        <ep> = <ep>.strip(); if <ep>: <acc>.add(<ep>)` — a value-DROPPED
    split/strip/truthy-add chain (the exact pieces are a value fact `ensures
    True` does not need); only the SHAPE is validated, fail-closed."""
    if not (isinstance(assign, dict) and assign.get("stmt") == "Assign"):
        return False
    v = assign.get("target")
    if not isinstance(v, str) or v in (hvar, acc):
        return False
    if _match_get_call(assign.get("value", {}), hvar) is None:
        return False
    if not (isinstance(ifblock, dict) and ifblock.get("stmt") == "If" and not ifblock.get("orelse")):
        return False
    if not _is_var(ifblock.get("test"), v):
        return False
    ibody = ifblock.get("body", [])
    if len(ibody) != 1:
        return False
    loop = ibody[0]
    if not (isinstance(loop, dict) and loop.get("stmt") == "For" and not loop.get("orelse")):
        return False
    it = loop.get("iter", {})
    if not (isinstance(it, dict) and it.get("type") == "Call" and it.get("func") == f"{v}.split"
            and len(it.get("args", [])) == 1 and _is_string(it["args"][0]) is not None):
        return False
    epvar = loop.get("target")
    lb2 = loop.get("body", [])
    if not isinstance(epvar, str) or epvar in (v, hvar, acc) or len(lb2) != 2:
        return False
    stripasg, addif = lb2
    if not (isinstance(stripasg, dict) and stripasg.get("stmt") == "Assign"
            and stripasg.get("target") == epvar):
        return False
    sv = stripasg.get("value", {})
    if not (isinstance(sv, dict) and sv.get("type") == "Call" and sv.get("func") == f"{epvar}.strip"
            and not sv.get("args")):
        return False
    if not (isinstance(addif, dict) and addif.get("stmt") == "If" and not addif.get("orelse")):
        return False
    if not _is_var(addif.get("test"), epvar):
        return False
    ab = addif.get("body", [])
    if len(ab) != 1:
        return False
    a0 = ab[0]
    if not (isinstance(a0, dict) and a0.get("stmt") == "Expr"):
        return False
    call = a0.get("value", {})
    return (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.add" and len(call.get("args", [])) == 1
            and _is_var(call["args"][0], epvar))


def _match_stmt_trywalk_arm(stmt: Any, stmtv: str, acc: str, fname: str,
                            extra: List[str]) -> Optional[str]:
    """Optional trywalk-arm:
        if <stmtv>.get("stmt") == "<TAG>":
            for <h> in <stmtv>.get("<key1>", []):
                <exc-split-add chain>            # _match_trywalk_exc_block
                <acc> |= self(<h>.get("<key2>", [])[, extra...])
    Every key (`TAG`, `key1`, `key2`) is read off the IR, not hardcoded.
    Returns the matched tag or None (fail-closed)."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "If" and not stmt.get("orelse")):
        return None
    tag = _match_stmt_tag_test(stmt.get("test", {}), stmtv)
    if tag is None:
        return None
    body = stmt.get("body", [])
    if len(body) != 1:
        return None
    loop = body[0]
    if not (isinstance(loop, dict) and loop.get("stmt") == "For" and not loop.get("orelse")):
        return None
    if _match_get_call(loop.get("iter", {}), stmtv) is None:
        return None
    hvar = loop.get("target")
    if not isinstance(hvar, str) or hvar in (acc, stmtv) or hvar in extra:
        return None
    lb = loop.get("body", [])
    if len(lb) != 3:
        return None
    assign, ifblock, unionstmt = lb
    if not _match_trywalk_exc_block(assign, ifblock, hvar, acc):
        return None
    if not (isinstance(unionstmt, dict) and unionstmt.get("stmt") == "AugAssign"
            and unionstmt.get("target") == acc and unionstmt.get("op") == "|"):
        return None
    uargs = _match_stmt_union_call(unionstmt.get("value", {}), acc, fname, extra)
    if uargs is None:
        return None
    if _match_get_call(uargs[0], hvar) is None:
        return None
    return tag


# ---- G-set-accumulate CTOR-MEMBERSHIP add-arm (`_collect_variant_var_assigns`)
#
# A third add-arm shape whose guard is a self-dict MEMBERSHIP over an interned
# field-name payload, expressed as a boolean local `is_ctor` bound to a
# DISJUNCTION of `(<val>.get("<tagkey>")=="<TAG>" and <val>.get("<memkey>") in
# <ctorsvar>)` clauses, where `<ctorsvar>` is a local bound in the method PREFIX
# to `getattr(self, "<field>", {})` (the self dict). The membership lowers to an
# OPAQUE `val function <field>_mem (k: string) : bool` over the read field-name
# string — a legitimate boundary reader (the `symtab_mem`/`_pred` opaque
# pattern), NOT an axiom, and NOT int-erased: the fold still reads the interned
# `<memkey>` payload string and gates the `set_add name` on the opaque
# membership predicate. Under `ensures True` the tag-eq is a pure boolean gate on
# WHICH names are added (the same insight-C scope-cut doctrine as every other
# shape here); the added name is the interned `stmt.get("<addkey>")` string, read
# faithfully into `SCons name`. Fail-closed exactly as the other arms.


def _flatten_or(node: Any) -> List[Any]:
    """Left-associatively flatten an `or`-tree into its disjunct list."""
    if (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "or"):
        return _flatten_or(node.get("left")) + _flatten_or(node.get("right"))
    return [node]


def _match_getattr_bind(stmt: Any) -> Optional[tuple]:
    """`<lv> = getattr(self, "<field>"[, default])` -> (lv, field) or None.
    The self-dict field bind whose local aliases a `self.<field>` dict."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Assign"):
        return None
    lv = stmt.get("target")
    if not isinstance(lv, str):
        return None
    val = stmt.get("value", {})
    if not (isinstance(val, dict) and val.get("type") == "Call"
            and val.get("func") == "getattr"):
        return None
    args = val.get("args", [])
    if len(args) < 2 or not _is_var(args[0], "self"):
        return None
    field = _is_string(args[1])
    if field is None:
        return None
    return (lv, field)


def _match_setinit(stmt: Any) -> Optional[str]:
    """`<acc> = set()` -> acc or None (the fresh returned-set accumulator)."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Assign"):
        return None
    acc = stmt.get("target")
    if not isinstance(acc, str):
        return None
    iv = stmt.get("value")
    if not (isinstance(iv, dict) and iv.get("type") == "Call"
            and iv.get("func") == "set" and not iv.get("args")):
        return None
    return acc


def _match_early_exit(stmt: Any, acc: str) -> bool:
    """`if <test>: return <acc>` (no else) — the no-op guard-return prefix that
    returns the STILL-EMPTY accumulator early. Recognised + SKIPPED: at prefix
    position `acc` is provably the empty `set()` (the loop is the only mutator),
    so dropping it yields a model that folds over the full domain (a superset)
    — sound under the `ensures True` type-safety-only contract, the same
    insight-C scope-cut doctrine as every other shape here. Fail-closed: the
    body MUST be exactly `return <acc>` (any other early-return value rejects)."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "If"):
        return False
    if stmt.get("orelse"):
        return False
    body = stmt.get("body", [])
    if len(body) != 1:
        return False
    r = body[0]
    return (isinstance(r, dict) and r.get("stmt") == "Return"
            and _is_var(r.get("value"), acc))


def _match_field_selfmem_guard(node: Any, valv: str,
                               ctors_fields: Dict[str, str]) -> Optional[tuple]:
    """`<valv>.get("<memkey>") in <ctorsvar>` -> (memkey, field) or None, where
    `<ctorsvar>` is a getattr-bound self-dict local (in `ctors_fields`)."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "in"):
        return None
    key = _match_get_call(node.get("left", {}), valv)
    if key is None:
        return None
    right = node.get("right", {})
    if not (_is_var(right) and right.get("name") in ctors_fields):
        return None
    return (key, ctors_fields[right.get("name")])


def _match_ctor_clause(node: Any, valv: str,
                       ctors_fields: Dict[str, str]) -> Optional[tuple]:
    """`<valv>.get("<tagkey>")=="<TAG>" and <valv>.get("<memkey>") in <ctorsvar>`
    -> (tag_key, tag_val, mem_key, field) or None (fail-closed)."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "and"):
        return None
    eq = _match_field_eq_guard(node.get("left", {}), valv)
    if eq is None:
        return None
    mem = _match_field_selfmem_guard(node.get("right", {}), valv, ctors_fields)
    if mem is None:
        return None
    return (eq[0], eq[1], mem[0], mem[1])


def _match_ctor_disjunction(node: Any, valv: str,
                            ctors_fields: Dict[str, str]) -> Optional[List[tuple]]:
    """A non-empty `or`-tree of ctor clauses (`_match_ctor_clause`) or None."""
    clauses: List[tuple] = []
    for d in _flatten_or(node):
        c = _match_ctor_clause(d, valv, ctors_fields)
        if c is None:
            return None
        clauses.append(c)
    return clauses or None


def _match_stmt_ctor_membership_arm(stmt: Any, stmtv: str, acc: str,
                                    ctors_fields: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Optional CTOR-MEMBERSHIP add-arm:
        if <stmt>.get("stmt") == "<TAG>":
            <val> = <stmt>.get("value", {})
            if isinstance(<val>, dict):
                <ctorvar> = (<clause> or <clause> or ...)   # ctor disjunction
                if <ctorvar>:
                    <tgt> = <stmt>.get("<addkey>", "")
                    if <tgt>: <acc>.add(<tgt>)
    Returns {kind:"ctor_membership", outer_tag, val_local, clauses, add_key} or
    None (fail-closed). Requires `ctors_fields` non-empty (a getattr self-dict
    bind must be in scope) — so a method without the prefix never matches."""
    if not ctors_fields:
        return None
    if not isinstance(stmt, dict) or stmt.get("stmt") != "If":
        return None
    if stmt.get("orelse"):
        return None
    outer_tag = _match_stmt_tag_test(stmt.get("test", {}), stmtv)
    if outer_tag is None:
        return None
    body = stmt.get("body", [])
    if len(body) != 2:
        return None
    asg = body[0]
    if not (isinstance(asg, dict) and asg.get("stmt") == "Assign"):
        return None
    valv = asg.get("target")
    if not isinstance(valv, str):
        return None
    if _match_get_call(asg.get("value", {}), stmtv) != "value":
        return None
    inner = body[1]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If"
            and not inner.get("orelse")):
        return None
    it = inner.get("test", {})
    if not (isinstance(it, dict) and it.get("type") == "Call"
            and it.get("func") == "isinstance" and len(it.get("args", [])) == 2
            and _is_var(it["args"][0], valv) and _is_var(it["args"][1], "dict")):
        return None
    ibody = inner.get("body", [])
    if len(ibody) != 2:
        return None
    cas = ibody[0]
    if not (isinstance(cas, dict) and cas.get("stmt") == "Assign"):
        return None
    ctorvar = cas.get("target")
    if not isinstance(ctorvar, str):
        return None
    clauses = _match_ctor_disjunction(cas.get("value", {}), valv, ctors_fields)
    if clauses is None:
        return None
    addif = ibody[1]
    if not (isinstance(addif, dict) and addif.get("stmt") == "If"
            and not addif.get("orelse") and _is_var(addif.get("test"), ctorvar)):
        return None
    add_key = _match_stmt_arm_add_body(addif.get("body", []), stmtv, acc)
    if add_key is None:
        return None
    return {"kind": "ctor_membership", "outer_tag": outer_tag,
            "val_local": valv, "clauses": clauses, "add_key": add_key}


def _selfmem_whyml_name(n: str, field: str) -> str:
    """WhyML-safe opaque self-dict membership predicate name for `field`."""
    return f"{n}__mem_" + "".join(c if c.isalnum() else "_" for c in field)


def recognize_stmt_setfold(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the G-set-accumulate-multiway statement-tree
    Set[str] fold (see the module note above). Returns
    {subject, acc_local, extra_params, stmtvar, pre_action|None} or None.
    Never raises."""
    try:
        return _recognize_stmt_setfold(func)
    except Exception:
        return None


def _recognize_stmt_setfold(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if not params:
        return None
    subj = params[0]
    extra = params[1:]
    pa = func.get("param_annotations", {})
    if pa.get(subj) != "list":
        return None
    for e in extra:
        if pa.get(e) != "set":
            return None
    if func.get("return_annotation") != "set":
        return None
    fname = func["name"]

    body = func.get("body", [])
    if len(body) < 3:
        return None
    # The tail is always `<loop>; return <acc>`; the head is a bounded PREFIX of
    # {the `<acc> = set()` init, optional `getattr(self,"<field>",{})` self-dict
    # binds, optional no-op early-exit guard-returns} in any order (init before
    # any early-exit). A method with NO prefix beyond the init reduces EXACTLY to
    # the historical 3-statement shape (byte-additive for every existing
    # consumer). See the ctor-membership module note above.
    loop, ret = body[-2], body[-1]
    prefix = body[:-2]
    acc: Optional[str] = None
    ctors_fields: Dict[str, str] = {}
    for st in prefix:
        si = _match_setinit(st)
        if si is not None:
            if acc is not None:
                return None
            acc = si
            continue
        ga = _match_getattr_bind(st)
        if ga is not None:
            ctors_fields[ga[0]] = ga[1]
            continue
        if acc is not None and _match_early_exit(st, acc):
            continue
        return None
    if acc is None or acc == subj or acc in extra:
        return None
    if not (isinstance(ret, dict) and ret.get("stmt") == "Return"
            and _is_var(ret.get("value"), acc)):
        return None
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"
            and not loop.get("orelse") and _is_var(loop.get("iter"), subj)):
        return None
    stmtv = loop.get("target")
    if not isinstance(stmtv, str) or stmtv in (acc, subj) or stmtv in extra:
        return None
    lbody = list(loop.get("body", []))
    if not lbody:
        return None

    # Elif-chain loop body (`find_ghost_vars`): the WHOLE loop body is one
    # If/orelse chain (add-arm + descend-arms fused, no separate unconditional
    # descend-loop). Tried first since it consumes ALL of `lbody` at once.
    if len(lbody) == 1 and isinstance(lbody[0], dict) and lbody[0].get("stmt") == "If":
        chain = _match_elif_chain(lbody[0], stmtv, acc, fname, extra)
        if chain is not None:
            return {"subject": subj, "acc_local": acc, "extra_params": extra,
                    "stmtvar": stmtv, "pre_action": chain}

    pre = None
    idx = 0
    maybe_pre = _match_stmt_add_arm(lbody[0], stmtv, acc, extra)
    if maybe_pre is None:
        maybe_pre = _match_chain_add_arm(lbody[0], stmtv, acc)
    if maybe_pre is None:
        maybe_pre = _match_stmt_direct_add_arm(lbody[0], stmtv, acc)
    if maybe_pre is None:
        maybe_pre = _match_stmt_ctor_membership_arm(lbody[0], stmtv, acc, ctors_fields)
    if maybe_pre is not None:
        pre = maybe_pre
        idx = 1

    # Optional trywalk-arm (`collect_user_exceptions`): a nested per-handler
    # walk between the simple add-arm and the required body/orelse descend
    # loop. Validated as SHAPE ONLY — see the G-set-accumulate-trywalk note
    # above — and contributes no separate emission.
    if idx < len(lbody) and _match_stmt_trywalk_arm(lbody[idx], stmtv, acc, fname, extra) is not None:
        idx += 1

    if idx >= len(lbody) or not _match_stmt_descend_loop(lbody[idx], stmtv, acc, fname, extra):
        return None
    idx += 1

    seen_echo_tags: set = set()
    while idx < len(lbody):
        tag = _match_echo_arm(lbody[idx], stmtv, acc, fname, extra)
        if tag is None or tag in seen_echo_tags:
            return None
        seen_echo_tags.add(tag)
        idx += 1

    return {"subject": subj, "acc_local": acc, "extra_params": extra,
            "stmtvar": stmtv, "pre_action": pre}


def emit_stmt_setfold_group(func: Dict[str, Any], desc: Dict[str, Any],
                            whyml_ident, top_ensures: Optional[List[str]] = None) -> List[str]:
    """Emit the G-set-accumulate-multiway Set[str] statement-tree fold for a
    recognized closure. Reuses the certified `pyval`/`pydict`/`size*` L1 theory
    and the purely-defined `set_add`/`set_union` `map string bool` algebra
    (`recognize_setfold`'s machinery) — a full-subtree OR-union catamorphism
    over `stmts: list pyval` (the `emit_bool_existence_group` walk shape,
    congruent modulo the `bool`->`map string bool`/`||`->`set_union` algebra
    swap), with an inlined pre-action reading the recognized add-arm's guards
    off the matched `PDict`. NO new WhyML theory, no new abstract op, no axiom."""
    n = whyml_ident(func["name"])
    extra = desc["extra_params"]
    pre = desc["pre_action"]
    extra_sig = "".join(f" ({whyml_ident(e)}: map string bool)" for e in extra)
    extra_args = "".join(f" {whyml_ident(e)}" for e in extra)
    out: List[str] = []
    _te = list(top_ensures or ["true"])

    reader_names: Dict[str, str] = {}
    # Opaque self-predicate declarations (`val function ... : bool`), prepended
    # to the group so they precede their use. Empty unless the add-arm carries a
    # `self.<pred>(val)` guard — keeps the emission byte-additive for every
    # existing (non-predicate) consumer.
    _pred_decls: List[str] = []

    def _emit_reader(key: str) -> str:
        if key in reader_names:
            return reader_names[key]
        rname = f"{n}__get_{_reader_suffix(key)}"
        reader_names[key] = rname
        out.append(f"  let rec {rname} (d: pydict) : option pyval")
        out.append("    variant { d }")
        out.append("  = match d with")
        out.append("    | DNil -> None")
        if key in _NAMED_KEYS:
            out.append(f"    | DCons {_NAMED_KEYS[key]} v _ -> Some v")
            out.append(f"    | DCons _ _ rest -> {rname} rest")
        else:
            out.append(f'    | DCons (K_dyn s) v rest -> if pystr_eq s "{key}" then Some v else {rname} rest')
            out.append(f"    | DCons _ _ rest -> {rname} rest")
        out.append("    end")
        return rname

    if pre is not None and pre.get("kind") == "direct":
        # find_ghost_vars elif-chain shape: `<acc>.add(<field-ref-on-stmt>)`,
        # no value-nesting, no guards — the simplest add-arm in the family.
        _emit_reader("stmt")
        _emit_reader(pre["add_key"])
        stmtr = reader_names["stmt"]
        addr = reader_names[pre["add_key"]]
        out.append(f"  let {n}__pre (d: pydict){extra_sig} : map string bool")
        out.append(f"  = match {stmtr} d with")
        out.append("    | Some (PStr tg0) ->")
        out.append(f'        if pystr_eq tg0 "{pre["outer_tag"]}" then')
        out.append(f"          (match {addr} d with")
        out.append("           | Some (PStr t) -> set_add (const false) t")
        out.append("           | _ -> const false end)")
        out.append("        else const false")
        out.append("    | _ -> const false end")
    elif pre is not None and pre.get("kind") == "chain":
        # find_append_targets chain shape: a MULTI-level literal-key
        # projection (`field_path`) reached through N nested nested-dict
        # guards; the terminal projection is the add source (the source's own
        # value-transform of it is dropped — a value fact `ensures True` does
        # not need, the same scope-cut doctrine as every other shape here).
        path = pre["field_path"]
        _emit_reader("stmt")
        for key in path:
            _emit_reader(key)
        stmtr = reader_names["stmt"]
        out.append(f"  let {n}__pre (d: pydict){extra_sig} : map string bool")
        out.append(f"  = match {stmtr} d with")
        out.append("    | Some (PStr tg0) ->")
        out.append(f'        if pystr_eq tg0 "{pre["outer_tag"]}" then')
        indent = "          "
        cur = "d"
        closers: List[str] = []
        for i, key in enumerate(path[:-1]):
            rname = reader_names[key]
            dv = f"d{i + 1}"
            out.append(f"{indent}(match {rname} {cur} with")
            out.append(f"{indent} | Some (PDict {dv}) ->")
            closers.append(f"{indent} | _ -> const false end)")
            indent += "     "
            cur = dv
        last = reader_names[path[-1]]
        out.append(f"{indent}(match {last} {cur} with")
        out.append(f"{indent} | Some (PStr t) -> set_add (const false) t")
        out.append(f"{indent} | _ -> const false end)")
        for cl in reversed(closers):
            out.append(cl)
        out.append("        else const false")
        out.append("    | _ -> const false end")
    elif pre is not None and pre.get("kind") == "ctor_membership":
        # `_collect_variant_var_assigns` shape: a self-dict MEMBERSHIP guard over
        # an interned field-name payload. Each disjunct `(<val>.get("<tagkey>")==
        # "<TAG>" and <val>.get("<memkey>") in <self.field>)` lowers to a
        # tag-eq `pystr_eq` gate conjoined with the OPAQUE `<field>_mem` membership
        # predicate applied to the READ field-name string — a boundary reader
        # (like `symtab_mem`), NOT an axiom, NOT int-erased. `is_ctor` is the
        # disjunction; when true the interned `stmt.get("<addkey>")` string is
        # added (`set_add name`).
        _emit_reader("stmt")
        _emit_reader("value")
        for (tk, _tv, mk, _field) in pre["clauses"]:
            _emit_reader(tk)
            _emit_reader(mk)
        _emit_reader(pre["add_key"])
        stmtr = reader_names["stmt"]
        valr = reader_names["value"]
        addr = reader_names[pre["add_key"]]
        seen_fields: set = set()
        for (_tk, _tv, _mk, field) in pre["clauses"]:
            memfn = _selfmem_whyml_name(n, field)
            if memfn not in seen_fields:
                seen_fields.add(memfn)
                _pred_decls.append(f"  val function {memfn} (k: string) : bool")
        clause_exprs: List[str] = []
        for i, (tk, tv, mk, field) in enumerate(pre["clauses"]):
            tagr = reader_names[tk]
            memr = reader_names[mk]
            memfn = _selfmem_whyml_name(n, field)
            clause_exprs.append(
                f'((match {tagr} vd with Some (PStr ct{i}) -> pystr_eq ct{i} "{tv}" | _ -> false end)'
                f" && (match {memr} vd with Some (PStr mn{i}) -> {memfn} mn{i} | _ -> false end))")
        is_ctor = " || ".join(clause_exprs)
        out.append(f"  let {n}__pre (d: pydict){extra_sig} : map string bool")
        out.append(f"  = match {stmtr} d with")
        out.append("    | Some (PStr tg0) ->")
        out.append(f'        if pystr_eq tg0 "{pre["outer_tag"]}" then')
        out.append(f"          (match {valr} d with")
        out.append("           | Some (PDict vd) ->")
        out.append(f"               if {is_ctor} then")
        out.append(f"                 (match {addr} d with")
        out.append("                  | Some (PStr t) -> set_add (const false) t")
        out.append("                  | _ -> const false end)")
        out.append("               else const false")
        out.append("           | _ -> const false end)")
        out.append("        else const false")
        out.append("    | _ -> const false end")
    elif pre is not None:
        _emit_reader("stmt")
        _emit_reader("value")
        for (_kind, gk, _gv) in pre["guards"]:
            _emit_reader(gk)
        _emit_reader(pre["add_key"])

        stmtr = reader_names["stmt"]
        valr = reader_names["value"]
        addr = reader_names[pre["add_key"]]
        out.append(f"  let {n}__pre (d: pydict){extra_sig} : map string bool")
        out.append(f"  = match {stmtr} d with")
        out.append("    | Some (PStr tg0) ->")
        out.append(f'        if pystr_eq tg0 "{pre["outer_tag"]}" then')
        out.append(f"          (match {valr} d with")
        out.append("           | Some (PDict vd) ->")
        indent = "               "
        closers: List[str] = []
        # Opaque self-predicate guards (`self._rhs_yields_map(val)`): an
        # uninterpreted bool over the isinstance-narrowed value pyval — a
        # boundary reader (like `symtab_mem`), NOT an axiom. It genuinely GATES
        # membership: a value the predicate rejects contributes `const false`.
        for meth in pre.get("preds", []):
            predfn = _pred_whyml_name(n, meth)
            _pred_decls.append(f"  val function {predfn} (v: pyval) : bool")
            out.append(f"{indent}if {predfn} (PDict vd) then")
            closers.append(f"{indent}else const false")
            indent += "  "
        for i, (kind, gk, gv) in enumerate(pre["guards"]):
            gname = reader_names[gk]
            gpat = f"gv{i}"
            out.append(f"{indent}(match {gname} vd with")
            if kind == "eq":
                out.append(f'{indent} | Some (PStr {gpat}) -> if pystr_eq {gpat} "{gv}" then')
            else:
                pname = whyml_ident(gv)
                out.append(f"{indent} | Some (PStr {gpat}) -> if Map.get {pname} {gpat} then")
            closers.append(f"{indent}   else const false | _ -> const false end)")
            indent += "   "
        out.append(f"{indent}(match {addr} d with")
        out.append(f"{indent} | Some (PStr t) -> set_add (const false) t")
        out.append(f"{indent} | _ -> const false end)")
        for cl in reversed(closers):
            out.append(cl)
        out.append("           | _ -> const false end)")
        out.append("        else const false")
        out.append("    | _ -> const false end")

    pre_term = (f"set_union ({n}__pre d{extra_args}) ({n}__d d{extra_args})"
                if pre is not None else f"{n}__d d{extra_args}")
    _ens_line = "".join(f" ensures {{ {e} }}" for e in _te)
    out.append(f"  let rec {n} (stmts: list pyval){extra_sig} : map string bool")
    out.append(f"    requires {{ true }}{_ens_line}")
    out.append("    variant { size_list stmts }")
    out.append("  = match stmts with")
    out.append(f"    | Nil -> const false")
    out.append(f"    | Cons h t -> set_union ({n}__v h{extra_args}) ({n} t{extra_args}) end")
    out.append(f"  with {n}__v (v: pyval){extra_sig} : map string bool")
    out.append("    requires { true } ensures { true } variant { pv_size v }")
    out.append("  = match v with")
    out.append(f"    | PDict d -> {pre_term}")
    out.append(f"    | PList xs -> {n} xs{extra_args}")
    out.append("    | _ -> const false end")
    out.append(f"  with {n}__d (d: pydict){extra_sig} : map string bool")
    out.append("    requires { true } ensures { true } variant { size_dict d }")
    out.append("  = match d with DNil -> const false")
    out.append(f"    | DCons _ v rest -> set_union ({n}__v v{extra_args}) ({n}__d rest{extra_args}) end")
    return _pred_decls + out


def recognize_frt(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the composed `find_return_type` (D + T2). Returns
    {subject, closures:[c1,c2]} or None. Never raises."""
    try:
        return _recognize_frt(func)
    except Exception:
        return None


def _recognize_frt(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    subj = params[0]
    if func.get("param_annotations", {}).get(subj) != "list":
        return None
    if func.get("return_annotation") != "str":
        return None
    body = func.get("body", [])
    if len(body) != 4:
        return None
    g1, g2, loop, tail = body
    # tail: return "int"
    if not (isinstance(tail, dict) and tail.get("stmt") == "Return"
            and _is_string(tail.get("value")) == "int"):
        return None
    # g1, g2: `if not <closure>(stmts): return "unit"`
    c1 = _match_unit_guard(g1, subj)
    c2 = _match_unit_guard(g2, subj)
    if c1 is None or c2 is None:
        return None
    # loop: for stmt in stmts: <value-tail arm> <descend arm> <cases arm>
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"
            and _is_var(loop.get("iter"), subj)):
        return None
    stmtv = loop.get("target")
    lbody = loop.get("body", [])
    if len(lbody) != 3:
        return None
    if not _match_frt_value_arm(lbody[0], stmtv):
        return None
    if not _match_frt_descend_arm(lbody[1], stmtv, func["name"]):
        return None
    if not _match_frt_cases_arm(lbody[2], stmtv, func["name"]):
        return None
    return {"subject": subj, "closures": [c1, c2]}


def _match_unit_guard(node: Any, subj: str) -> Optional[str]:
    """`if not <closure>(<subj>): return "unit"` -> closure bare name or None."""
    if not (isinstance(node, dict) and node.get("stmt") == "If" and not node.get("orelse")):
        return None
    test = node.get("test", {})
    if not (isinstance(test, dict) and test.get("type") == "UnaryOp"
            and test.get("op") == "not"):
        return None
    call = test.get("expr", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and isinstance(call.get("func"), str)
            and len(call.get("args", [])) == 1 and _is_var(call["args"][0], subj)):
        return None
    b = node.get("body", [])
    if not (len(b) == 1 and isinstance(b[0], dict) and b[0].get("stmt") == "Return"
            and _is_string(b[0].get("value")) == "unit"):
        return None
    return call["func"]


def _match_frt_value_arm(node: Any, stmtv: str) -> bool:
    """`if <stmt>["stmt"]=="Return" and <stmt>.get("value"): val=<stmt>["value"];
        if val.get("type")=="Tuple": ... return "("+join+")"; if ..=="String": return "int"`.
    Structural markers only (value production is unconstrained under ensures True)."""
    if not (isinstance(node, dict) and node.get("stmt") == "If" and not node.get("orelse")):
        return False
    test = node.get("test", {})
    if not (isinstance(test, dict) and test.get("type") == "BinOp" and test.get("op") == "and"):
        return False
    if _match_stmt_tag_test(test.get("left", {}), stmtv) != "Return":
        return False
    if _match_get_call(test.get("right", {}), stmtv) != "value":
        return False
    b = node.get("body", [])
    # val = stmt["value"]; then >=1 type-dispatch Ifs. Require the val assign + a
    # Tuple arm producing a join, and a String arm.
    if len(b) < 2:
        return False
    asg = b[0]
    if not (isinstance(asg, dict) and asg.get("stmt") == "Assign"
            and _match_subscript_str(asg.get("value"), stmtv) == "value"):
        return False
    valv = asg.get("target")
    saw_tuple = saw_string = False
    for st in b[1:]:
        if not (isinstance(st, dict) and st.get("stmt") == "If"):
            return False
        vtag = _match_valtype_test(st.get("test", {}), valv)
        if vtag == "Tuple" and _arm_returns_join(st.get("body", [])):
            saw_tuple = True
        elif vtag == "String":
            saw_string = True
        else:
            return False
    return saw_tuple and saw_string


def _match_valtype_test(test: Any, valv: str) -> Optional[str]:
    """`<valv>.get("type") == "<TAG>"` -> TAG."""
    if not (isinstance(test, dict) and test.get("type") == "BinOp" and test.get("op") == "=="):
        return None
    if _match_get_call(test.get("left", {}), valv) != "type":
        return None
    return _is_string(test.get("right"))


def _arm_returns_join(stmts: Any) -> bool:
    """The Tuple arm ends in a `return "(" + ", ".join([...]*n) + ")"` (a join call
    somewhere in the returned expr). Loose structural check (value unconstrained)."""
    def _has_join(node: Any) -> bool:
        if isinstance(node, dict):
            if node.get("type") == "Call" and node.get("func") == "join":
                return True
            return any(_has_join(v) for v in node.values())
        if isinstance(node, list):
            return any(_has_join(x) for x in node)
        return False
    if not (isinstance(stmts, list) and stmts):
        return False
    ret = stmts[-1]
    return (isinstance(ret, dict) and ret.get("stmt") == "Return"
            and _has_join(ret.get("value")))


def _match_frt_descend_arm(node: Any, stmtv: str, fname: str) -> bool:
    """`for key in ("body","orelse"): if key in stmt: result=self(stmt[key]);
        if result not in ("int","unit"): return result`."""
    if not (isinstance(node, dict) and node.get("stmt") == "For"):
        return False
    it = node.get("iter", {})
    keys = [_is_string(e) for e in it.get("elts", [])] if isinstance(it, dict) else []
    if keys != ["body", "orelse"]:
        return False
    keyv = node.get("target")
    lb = node.get("body", [])
    if len(lb) != 1:
        return False
    iff = lb[0]
    if not (isinstance(iff, dict) and iff.get("stmt") == "If" and not iff.get("orelse")):
        return False
    test = iff.get("test", {})
    if not (isinstance(test, dict) and test.get("type") == "BinOp" and test.get("op") == "in"
            and _is_var(test.get("left"), keyv) and _is_var(test.get("right"), stmtv)):
        return False
    return _match_result_dispatch(iff.get("body", []), fname,
                                  lambda a: (isinstance(a, dict) and a.get("type") == "Subscript"
                                             and _is_var(a.get("value"), stmtv)
                                             and _is_var(a.get("index"), keyv)))


def _match_frt_cases_arm(node: Any, stmtv: str, fname: str) -> bool:
    """`if stmt.get("stmt")=="Match": for c in stmt.get("cases",[]):
        result=self(c.get("body",[])); if result not in ("int","unit"): return result`."""
    if not (isinstance(node, dict) and node.get("stmt") == "If" and not node.get("orelse")):
        return False
    if _match_stmt_tag_test(node.get("test", {}), stmtv) != "Match":
        return False
    cb = node.get("body", [])
    if len(cb) != 1:
        return False
    loop = cb[0]
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"):
        return False
    if _match_get_call(loop.get("iter", {}), stmtv) != "cases":
        return False
    cvar = loop.get("target")
    return _match_result_dispatch(loop.get("body", []), fname,
                                  lambda a: _match_get_call(a, cvar) == "body")


def _match_result_dispatch(stmts: Any, fname: str, arg_ok) -> bool:
    """`result = <self-recursion>(<arg>); if result not in ("int","unit"): return result`.
    `arg_ok(argnode)` validates the recursion argument shape."""
    if not (isinstance(stmts, list) and len(stmts) == 2):
        return False
    asg, iff = stmts
    if not (isinstance(asg, dict) and asg.get("stmt") == "Assign"):
        return False
    resv = asg.get("target")
    call = asg.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return False
    # the self-recursion is `IRScanner.find_return_type` -> canonicalizes to fname
    if _canon_call(str(call.get("func"))) != fname:
        return False
    if len(call.get("args", [])) != 1 or not arg_ok(call["args"][0]):
        return False
    if not (isinstance(iff, dict) and iff.get("stmt") == "If" and not iff.get("orelse")):
        return False
    test = iff.get("test", {})
    if not (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "not in" and _is_var(test.get("left"), resv)):
        return False
    rt = test.get("right", {})
    if not (isinstance(rt, dict) and rt.get("type") == "Tuple"):
        return False
    if [_is_string(e) for e in rt.get("elts", [])] != ["int", "unit"]:
        return False
    rb = iff.get("body", [])
    return (len(rb) == 1 and isinstance(rb[0], dict) and rb[0].get("stmt") == "Return"
            and _is_var(rb[0].get("value"), resv))


def emit_frt_group(func: Dict[str, Any], desc: Dict[str, Any],
                   whyml_ident) -> List[str]:
    """Emit the composed `find_return_type` group (D + T2): the shared helpers,
    the value-tail option producer (with the certified string tail), and the
    mutually-recursive first-match search glued to the two outlined bool folds."""
    n = whyml_ident(func["name"])
    cls = func["name"].split("__", 1)[0]
    c1 = whyml_ident(f"{cls}__{desc['closures'][0]}")
    c2 = whyml_ident(f"{cls}__{desc['closures'][1]}")
    out = _emit_stmt_reader(n)
    # extra readers for the value-tail production
    out.append(f"  let rec {n}__get_value (d: pydict) : option pyval")
    out.append("    variant { d }")
    out.append("  = match d with DNil -> None | DCons K_value v _ -> Some v")
    out.append(f"    | DCons _ _ rest -> {n}__get_value rest end")
    out.append(f"  let rec {n}__get_type (d: pydict) : option string")
    out.append("    variant { d }")
    out.append("  = match d with DNil -> None | DCons K_type (PStr s) _ -> Some s")
    out.append(f"    | DCons K_type _ _ -> None | DCons _ _ rest -> {n}__get_type rest end")
    out.append(f"  let rec {n}__get_elts (d: pydict) : list pyval")
    out.append("    variant { d }")
    out.append("  = match d with DNil -> Nil")
    out.append(f'    | DCons (K_dyn k) (PList xs) rest -> if pystr_eq k "elts" then xs else {n}__get_elts rest')
    out.append(f"    | DCons _ _ rest -> {n}__get_elts rest end")
    out.append(f"  let rec {n}__llen (xs: list pyval) : int")
    out.append("    ensures { result >= 0 } variant { xs }")
    out.append(f"  = match xs with Nil -> 0 | Cons _ t -> 1 + {n}__llen t end")
    out.append(f"  let function {n}__is_int_or_unit (s: string) : bool")
    out.append('  = pystr_eq s "int" || pystr_eq s "unit"')
    # value-tail: option string (the Tuple/String production incl. string tail)
    out.append(f"  let function {n}__value_tail (stmt: pyval) : option string")
    out.append("  = match stmt with")
    out.append("    | PDict d ->")
    out.append(f'        if {n}__stmt_is stmt "Return" then')
    out.append(f"          (match {n}__get_value d with")
    out.append("           | Some (PDict vd) ->")
    out.append(f"               (match {n}__get_type vd with")
    out.append("                | Some t ->")
    out.append('                    if pystr_eq t "Tuple" then')
    out.append(f"                      let nn = {n}__llen ({n}__get_elts vd) in")
    out.append('                      Some (str_concat_op (str_concat_op "(" (str_join_arr ", " (Array.make nn "int"))) ")")')
    out.append('                    else if pystr_eq t "String" then Some "int"')
    out.append("                    else None")
    out.append("                | None -> None end)")
    out.append("           | _ -> None end)")
    out.append("        else None")
    out.append("    | _ -> None end")
    # the composed group — universal-walk descent (direct structural sub-terms
    # for the recursion, so `variant`s decrease syntactically; split_vc-robust).
    # `find_return_type` (guard wrapper) -> `__search` uses the lexicographic
    # second component (1 vs 0) for the same-size edge; the child descent
    # (`__child`/`__child_d`) mirrors `find_return_type(stmt[key])` by re-running
    # the full guarded `find_return_type` on any nested list.
    out.append(f"  let rec {n} (stmts: list pyval) : string")
    out.append("    requires { true } ensures { true } variant { size_list stmts, 1 }")
    out.append(f"  = if not ({c1} stmts) then \"unit\"")
    out.append(f"    else if not ({c2} stmts) then \"unit\"")
    out.append(f"    else {n}__search stmts")
    out.append(f"  with {n}__search (stmts: list pyval) : string")
    out.append("    requires { true } ensures { true } variant { size_list stmts, 0 }")
    out.append("  = match stmts with Nil -> \"int\"")
    out.append("    | Cons stmt rest ->")
    out.append(f"        match {n}__value_tail stmt with")
    out.append("        | Some s -> s")
    out.append("        | None ->")
    out.append(f"            let r = {n}__child stmt in")
    out.append(f"            if not ({n}__is_int_or_unit r) then r else {n}__search rest")
    out.append("        end")
    out.append("    end")
    out.append(f"  with {n}__child (v: pyval) : string")
    out.append("    requires { true } ensures { true } variant { pv_size v, 0 }")
    out.append("  = match v with")
    out.append(f"    | PDict d -> {n}__child_d d")
    out.append(f"    | PList xs -> {n} xs")
    out.append("    | _ -> \"int\" end")
    out.append(f"  with {n}__child_d (d: pydict) : string")
    out.append("    requires { true } ensures { true } variant { size_dict d, 0 }")
    out.append("  = match d with DNil -> \"int\"")
    out.append("    | DCons _ v rest ->")
    out.append(f"        let r = {n}__child v in")
    out.append(f"        if not ({n}__is_int_or_unit r) then r else {n}__child_d rest end")
    return out


# ============================================================================
# ir-traversal-residual T3 — env-threaded fold + `sdict` + source-level raise
# (plan §5 / §6.2). The context-threading residual shape `_sa_walk(node, where,
# symtab)`: a walk that threads a read-only symbol table (`symtab`) and a
# context string (`where`) down the descent, reads `symtab.get(<computed-key>)`,
# and `raise`s `PyCSLSemanticError` on a mismatch. The env does NOT affect
# termination — the `variant` stays `size node` (an inherited attribute).
# ============================================================================

def _match_sa_selfrec3(stmt: Any, fname: str, p1: str, p2: str) -> bool:
    """`<self>(<any-var>, <p1>, <p2>)` as an ExprStmt — the 3-arg env-threaded
    self-recursion (`_sa_walk(v, where, symtab)`); the two trailing args are the
    read-only threaded env (`where`, `symtab`) passed VERBATIM."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Expr"):
        return False
    call = stmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return False
    if not _call_is_self(call.get("func"), fname):
        return False
    args = call.get("args", [])
    return (len(args) == 3 and _is_var(args[0])
            and _is_var(args[1], p1) and _is_var(args[2], p2))


def _match_sa_values_loop(stmt: Any, subj: str, fname: str, p1: str, p2: str) -> bool:
    """`for v in <subj>.values(): <self>(v, p1, p2)`."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "For"):
        return False
    it = stmt.get("iter", {})
    if not (isinstance(it, dict) and it.get("type") == "Call"
            and it.get("func") == f"{subj}.values" and not it.get("args")):
        return False
    body = stmt.get("body", [])
    return len(body) == 1 and _match_sa_selfrec3(body[0], fname, p1, p2)


def _match_sa_list_loop(stmt: Any, subj: str, fname: str, p1: str, p2: str) -> bool:
    """`for x in <subj>: <self>(x, p1, p2)`."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "For"):
        return False
    if not _is_var(stmt.get("iter"), subj):
        return False
    body = stmt.get("body", [])
    return len(body) == 1 and _match_sa_selfrec3(body[0], fname, p1, p2)


def _match_sa_raise(stmt: Any) -> Optional[str]:
    """A `raise <Exc>(...)` statement — returns the exception type name."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Raise"):
        return None
    exc = stmt.get("exc_type")
    return exc if isinstance(exc, str) else None


def _match_sa_pre(inner_if: Any, subj: str, symparam: str) -> Optional[Dict[str, Any]]:
    """Match the ArraySet pre-action guard (the computed-key symtab read + the
    two mismatch raises) and extract its data. Shape:

        if <subj>.get("stmt") == "<TAG>":
            arr = <subj>.get("<ARRAY_KEY>")
            if isinstance(arr, dict) and arr.get("<TYPE_KEY>") == "<TYPE_VAL>":
                name = arr.get("<NAME_KEY>")
                arr_type = <symparam>.get(name)
                if arr_type is None: raise <Exc>(...)
                if arr_type not in (<S0>, <S1>, ...): raise <Exc>(...)

    Returns {tag, array_key, type_key, type_val, name_key, ok_types, exc} or None.
    """
    if not (isinstance(inner_if, dict) and inner_if.get("stmt") == "If"
            and not inner_if.get("orelse")):
        return None
    tag = _match_stmt_tag_test(inner_if.get("test", {}), subj)
    if tag is None:
        return None
    ibody = inner_if.get("body", [])
    if len(ibody) != 2:
        return None
    # [0] arr = <subj>.get("<ARRAY_KEY>")
    a0 = ibody[0]
    if not (isinstance(a0, dict) and a0.get("stmt") == "Assign"):
        return None
    arrvar = a0.get("target")
    array_key = _match_get_call(a0.get("value", {}), subj)
    if not isinstance(arrvar, str) or array_key is None:
        return None
    # [1] the `isinstance(arr, dict) and arr.get("<TYPE_KEY>") == "<TYPE_VAL>"` If
    a1 = ibody[1]
    if not (isinstance(a1, dict) and a1.get("stmt") == "If" and not a1.get("orelse")):
        return None
    t1 = a1.get("test", {})
    if not (isinstance(t1, dict) and t1.get("type") == "BinOp" and t1.get("op") == "and"):
        return None
    if not _match_isinstance(t1.get("left", {}), arrvar, "dict"):
        return None
    tr = t1.get("right", {})
    if not (isinstance(tr, dict) and tr.get("type") == "BinOp" and tr.get("op") == "=="):
        return None
    type_val = _is_string(tr.get("right"))
    type_key = _match_get_call(tr.get("left", {}), arrvar)
    if type_val is None or type_key is None:
        return None
    gbody = a1.get("body", [])
    if len(gbody) != 4:
        return None
    # [0] name = arr.get("<NAME_KEY>")
    g0 = gbody[0]
    if not (isinstance(g0, dict) and g0.get("stmt") == "Assign"):
        return None
    namevar = g0.get("target")
    name_key = _match_get_call(g0.get("value", {}), arrvar)
    if not isinstance(namevar, str) or name_key is None:
        return None
    # [1] arr_type = <symparam>.get(name)
    g1 = gbody[1]
    if not (isinstance(g1, dict) and g1.get("stmt") == "Assign"):
        return None
    atvar = g1.get("target")
    gv = g1.get("value", {})
    if not (isinstance(gv, dict) and gv.get("type") == "Call"
            and gv.get("func") == f"{symparam}.get"):
        return None
    gargs = gv.get("args", [])
    if not (isinstance(atvar, str) and len(gargs) == 1 and _is_var(gargs[0], namevar)):
        return None
    # [2] if arr_type is None: raise <Exc>
    g2 = gbody[2]
    if not (isinstance(g2, dict) and g2.get("stmt") == "If" and not g2.get("orelse")):
        return None
    t2 = g2.get("test", {})
    if not (isinstance(t2, dict) and t2.get("type") == "BinOp" and t2.get("op") == "=="
            and _is_var(t2.get("left"), atvar)
            and isinstance(t2.get("right"), dict) and t2["right"].get("type") == "None"):
        return None
    g2b = g2.get("body", [])
    if len(g2b) != 1:
        return None
    exc = _match_sa_raise(g2b[0])
    if exc is None:
        return None
    # [3] if arr_type not in (<S0>, ...): raise <Exc>
    g3 = gbody[3]
    if not (isinstance(g3, dict) and g3.get("stmt") == "If" and not g3.get("orelse")):
        return None
    t3 = g3.get("test", {})
    if not (isinstance(t3, dict) and t3.get("type") == "BinOp" and t3.get("op") == "not in"
            and _is_var(t3.get("left"), atvar)):
        return None
    tup = t3.get("right", {})
    if not (isinstance(tup, dict) and tup.get("type") == "Tuple"):
        return None
    ok_types = [_is_string(e) for e in tup.get("elts", [])]
    if not ok_types or any(s is None for s in ok_types):
        return None
    g3b = g3.get("body", [])
    if len(g3b) != 1 or _match_sa_raise(g3b[0]) != exc:
        return None
    return {"tag": tag, "array_key": array_key, "type_key": type_key,
            "type_val": type_val, "name_key": name_key,
            "ok_types": ok_types, "exc": exc}


def recognize_sawalk(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the T3 context-threading walk `_sa_walk(node, where,
    symtab)` (plan §5). Returns a descriptor or None; never raises."""
    try:
        return _recognize_sawalk(func)
    except Exception:
        return None


def _recognize_sawalk(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 3:
        return None
    subj, p1, p2 = params[0], params[1], params[2]
    if func.get("return_annotation") not in ("None", None):
        return None
    fname = func["name"]
    body = func.get("body", [])
    if len(body) != 1:
        return None
    outer = body[0]
    if not (isinstance(outer, dict) and outer.get("stmt") == "If"):
        return None
    if not _match_isinstance(outer.get("test", {}), subj, "dict"):
        return None
    # dict-arm: exactly [pre-action If, values loop]
    dbody = outer.get("body", [])
    if len(dbody) != 2:
        return None
    pre = _match_sa_pre(dbody[0], subj, p2)
    if pre is None:
        return None
    if not _match_sa_values_loop(dbody[1], subj, fname, p1, p2):
        return None
    # else-arm: exactly `if isinstance(node, list): for x in node: self(x, p1, p2)`
    orelse = outer.get("orelse", [])
    if len(orelse) != 1:
        return None
    inner = orelse[0]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If" and not inner.get("orelse")):
        return None
    if not _match_isinstance(inner.get("test", {}), subj, "list"):
        return None
    ibody = inner.get("body", [])
    if len(ibody) != 1 or not _match_sa_list_loop(ibody[0], subj, fname, p1, p2):
        return None
    return {"subject": subj, "env1": p1, "env2": p2, "pre": pre}


def _sa_reader_lines(n: str, key: str, as_str: bool) -> List[str]:
    """Emit a spine reader `pydict -> option (string|pyval)` for `key`, using the
    interned constructor for a named key (zero string theory) or the `K_dyn s`
    fallback with a `pystr_eq` payload test for a computed key."""
    suf = _reader_suffix(key)
    rty = "option string" if as_str else "option pyval"
    out = [f"  let rec {n}__get_{suf} (d: pydict) : {rty}",
           "    variant { d }",
           "  = match d with",
           "    | DNil -> None"]
    if key in _NAMED_KEYS:
        hit = "(PStr s) _ -> Some s" if as_str else "v _ -> Some v"
        out.append(f"    | DCons {_NAMED_KEYS[key]} {hit}")
        out.append(f"    | DCons _ _ rest -> {n}__get_{suf} rest")
    elif as_str:
        out.append(f'    | DCons (K_dyn k) (PStr s) rest -> if pystr_eq k "{key}" then Some s else {n}__get_{suf} rest')
        out.append(f"    | DCons _ _ rest -> {n}__get_{suf} rest")
    else:
        out.append(f'    | DCons (K_dyn k) v rest -> if pystr_eq k "{key}" then Some v else {n}__get_{suf} rest')
        out.append(f"    | DCons _ _ rest -> {n}__get_{suf} rest")
    out.append("    end")
    return out


def emit_sawalk_group(func: Dict[str, Any], sa: Dict[str, Any],
                      whyml_ident) -> List[str]:
    """Emit the T3 env-threaded walk group for a recognized `_sa_walk`.

    The env (`where: string`, `symtab: sdict`) is threaded read-only down the
    `pyval`/`pydict`/`list pyval` catamorphism; the `variant` is `size node`
    (the env does not affect termination). The computed-key symbol-table read is
    `slookup name symtab : option pyval` — a total, option-valued lookup over the
    string-keyed `sdict` (defensive totalization); which entry is found is a
    value question no VC constrains (insight C: `pystr_eq`'s result is
    unconstrained). A mismatch `raise`s the source exception, declared `raises
    { <Exc> }` on every function in the group (exceptions are inside
    `why3_implements_wp_w`, axiom 3 — the ledger does not move)."""
    n = whyml_ident(func["name"])
    subj = sa["subject"]
    p1, p2 = sa["env1"], sa["env2"]
    pre = sa["pre"]
    exc = pre["exc"]  # already a valid WhyML exception ident (user_exceptions)
    out: List[str] = []
    # ---- spine readers for the pre-action's computed/interned keys ----
    out += _sa_reader_lines(n, "stmt", as_str=True)
    out += _sa_reader_lines(n, pre["array_key"], as_str=False)
    out += _sa_reader_lines(n, pre["type_key"], as_str=True)
    out += _sa_reader_lines(n, pre["name_key"], as_str=True)
    # ---- ok-type membership (semantic guard, insight C: result unconstrained) ----
    cond = " || ".join(f'pystr_eq s "{t}"' for t in pre["ok_types"])
    out.append(f"  let function {n}__ok_type (s: string) : bool = {cond}")
    # ---- the pre-action: the computed-key symtab read + the two mismatch raises ----
    stmt_suf = _reader_suffix("stmt")
    arr_suf = _reader_suffix(pre["array_key"])
    type_suf = _reader_suffix(pre["type_key"])
    name_suf = _reader_suffix(pre["name_key"])
    out.append(f"  let {n}__pre ({subj}: pyval) ({p2}: sdict) : unit")
    out.append(f"    raises {{ {exc} }}")
    out.append(f"  = match {subj} with")
    out.append("    | PDict d ->")
    out.append(f"        (match {n}__get_{stmt_suf} d with")
    out.append(f'         | Some st -> if pystr_eq st "{pre["tag"]}" then')
    out.append(f"             (match {n}__get_{arr_suf} d with")
    out.append("              | Some (PDict ad) ->")
    out.append(f"                  (match {n}__get_{type_suf} ad with")
    out.append(f'                   | Some ty -> if pystr_eq ty "{pre["type_val"]}" then')
    out.append(f"                       (match {n}__get_{name_suf} ad with")
    out.append(f"                        | Some nm ->")
    out.append(f"                            (match slookup nm {p2} with")
    out.append(f"                             | None -> raise {exc}")
    out.append(f"                             | Some (PStr aty) -> if {n}__ok_type aty then () else raise {exc}")
    out.append(f"                             | Some _ -> raise {exc}")
    out.append("                             end)")
    out.append("                        | None -> () end)")
    out.append("                     else ()")
    out.append("                   | None -> () end)")
    out.append("              | _ -> () end)")
    out.append("           else ()")
    out.append("         | None -> () end)")
    out.append("    | _ -> () end")
    # ---- the env-threaded walk / walk_dict / walk_list group ----
    out.append(f"  let rec {n} ({subj}: pyval) ({p1}: string) ({p2}: sdict) : unit")
    out.append(f"    requires {{ true }} ensures {{ true }} raises {{ {exc} }}")
    out.append(f"    variant {{ pv_size {subj} }}")
    out.append(f"  = match {subj} with")
    out.append(f"    | PDict d -> {n}__pre {subj} {p2}; {n}__dict d {p1} {p2}")
    out.append(f"    | PList xs -> {n}__list xs {p1} {p2}")
    out.append("    | _ -> () end")
    out.append(f"  with {n}__dict (d: pydict) ({p1}: string) ({p2}: sdict) : unit")
    out.append(f"    requires {{ true }} ensures {{ true }} raises {{ {exc} }}")
    out.append("    variant { size_dict d }")
    out.append("  = match d with")
    out.append("    | DNil -> ()")
    out.append(f"    | DCons _ v rest -> {n} v {p1} {p2}; {n}__dict rest {p1} {p2}")
    out.append("    end")
    out.append(f"  with {n}__list (xs: list pyval) ({p1}: string) ({p2}: sdict) : unit")
    out.append(f"    requires {{ true }} ensures {{ true }} raises {{ {exc} }}")
    out.append("    variant { size_list xs }")
    out.append(f"  = match xs with Nil -> () | Cons h t -> {n} h {p1} {p2}; {n}__list t {p1} {p2} end")
    return out


# =========================================================================
# alist-adict-census §3 (the ONE marginal A-dict opportunity) — the
# returned-`sdict` DICT-FOLD result algebra (result_algebra = a string-keyed
# dict, by RETURN). The by-KEY-grouping twin of the A-set returned-set fold.
#
# The two live methods (`find_record_var_classes`, `_collect_tuple_array_locals`)
# are clean structural folds that build a dict keyed by a RUNTIME string
# (`out[<x>.get("target")] = <value>`) and merge the recursive descents with
# `out.update(self(<child>, …))`. L1 `pydict` does NOT model them (its keys are
# interned `irkey` constructors); they need the already-certified `sdict`
# (Phase C, `Phase2c_PyValDict.v` / `PyValDict.lean`, the 2nd/last certificate)
# whose keys are runtime strings. The merge combinator is the purely-DEFINED
# `sappend` (list concat over the certified datatype — no axiom, totality
# discharged by Why3, exactly as `set_union` was for A-set); the 3-axiom ledger
# is UNCHANGED and no new certificate is needed.
#
# The emitted group is the FUNCTIONAL generic pyval walk (`assigns \nothing`; no
# `writes`), entered on the `list pyval` of statements: `build`/`build_val`/
# `build_dict` each return `sdict`, combined by `sappend`, `variant { size … }`
# over the L1 measure — congruent (modulo names / sdict-for-set) to the proven
# `v2_setfold_spike`. The per-node pre-action reads the runtime-string KEY
# (`<x>.get("target")` -> `Some (PStr k)` -> `k`) and inserts one `SCons k <val>`
# cell under the stmt-tag structural discriminant (a `pystr_eq` boolean gate no
# VC constrains, insight C).
#
# SCOPE-CUT (honest, type-safety-only, under the fixed `ensures True` contract,
# same discipline as the T1 note above):
#   * The walk visits ALL dict/list children (the generic pyval catamorphism),
#     a SUPERSET of the source's specific `body`/`orelse`/cases/handlers descent.
#     Collecting entries at more nodes is sound under type-safety-only (the
#     result stays a well-typed `(string, PStr|PInt)` sdict).
#   * For a STRING-valued dict the inserted value is read faithfully
#     (`<x>.get("value").get("func")`, gated on membership in the threaded set);
#     for an INT-valued dict the source value is a COMPUTED arity (a list
#     comprehension + set-cardinality the contract does not need), modelled as a
#     placeholder `PInt 0` — a value-refinement `ensures True` makes irrelevant.
#
# FLAT TWIN (`_recognize_flat_strdictfold` / `value.kind == "str1"`, `tag is None`):
# a NON-recursive collector `out={}; for x in <list>: v = x.get("<vkey>"); if v:
# out[x["<kkey>"]] = v; return out` — no `.update(self(…))` merge, no stmt-tag
# guard, the KEY is an inline subscript `x["<kkey>"]` and the VALUE a NO-DEFAULT
# `.get` (string). Discriminated from the recursive fold by that inline-subscript
# key. The value is read FAITHFULLY (`get_<vkey>` -> `Some (PStr v)` -> `SCons k
# (PStr v)`); the `if v:` truthiness is modelled by the `Some (PStr v)` arm (the
# empty-string refinement is a value fact `ensures True` does not need). The
# emitted catamorphism still visits ALL children — a SUPERSET of the source's
# single-level `for x in <list>` scan, sound under type-safety-only exactly as
# above. Only the str-typed value dict is taken (`dict_value_types[acc]=="string"`),
# tying the emitted `PStr` to the inferred value type. Gated by `needs_sdict`
# (`recognize_dictfold` covers both twins), so corpus emission stays byte-identical.
# (`_build_method_return_annotation_map`; observational fixture 0912.)
#
# Fail-closed exactly as the other folds: a miss keeps the method `\trusted`; a
# template bug yields an unprovable instance (the full-file re-proof is loud),
# never a false proof. Verified inert on the reference corpus (byte-diff 0); a
# poisoned control is the single external match that flips the gate red once.
# =========================================================================


def _iter_dict_nodes(node: Any):
    """Yield every dict node in the IR subtree rooted at `node` (pre-order)."""
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from _iter_dict_nodes(v)
    elif isinstance(node, list):
        for x in node:
            yield from _iter_dict_nodes(x)


def _match_acc_update_self(stmt: Any, acc: str, fname: str) -> bool:
    """`<acc>.update(<self>(<child>, …))` as an ExprStmt — the merge fold."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Expr"):
        return False
    call = stmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == f"{acc}.update"):
        return False
    args = call.get("args", [])
    if len(args) != 1:
        return False
    inner = args[0]
    return (isinstance(inner, dict) and inner.get("type") == "Call"
            and _call_is_self(inner.get("func"), fname))


def _recognize_flat_strdictfold(
        func: Dict[str, Any], subj: str, acc: str, x: str, key_key: str,
        aset: Dict[str, Any], lbody: List[Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the FLAT string-value dict collector (census §3 flat
    twin): `out={}; for x in <listparam>: v = x.get("<vkey>"); if v: out[x["<kkey>"]]
    = v; return out`. No self-merge, no stmt-tag guard, no threaded set; the value
    is read by a NO-DEFAULT `.get` (string), the key by an inline subscript."""
    # no threaded set — the sole formal must be the subject list.
    if [p for p in func.get("formal_params", []) if p != subj]:
        return None
    # value must be a str-typed dict AND read via a `if <vloc>:`-guarded local.
    if (func.get("dict_value_types") or {}).get(acc) != "string":
        return None
    vexpr = aset.get("value", {})
    if not _is_var(vexpr):
        return None
    vloc = vexpr["name"]
    # `<vloc> = <x>.get("<vkey>")` — NO-DEFAULT get, somewhere in the loop body.
    vkey = None
    for s in _iter_dict_nodes(lbody):
        if s.get("stmt") == "Assign" and s.get("target") == vloc:
            vkey = _match_get_call(s.get("value", {}), x)
            break
    if vkey is None:
        return None
    # the insert MUST be guarded by `if <vloc>:` (truthiness of the read value),
    # no orelse — a different guard/direction fails closed (stays \trusted).
    guarded = any(
        s.get("stmt") == "If" and not s.get("orelse")
        and _is_var(s.get("test"), vloc)
        and any(a is aset for a in _iter_dict_nodes(s.get("body", [])))
        for s in _iter_dict_nodes(lbody))
    if not guarded:
        return None
    return {"subject": subj, "extra_params": [], "acc": acc,
            "guard_key": None, "tag": None, "key_key": key_key,
            "value": {"kind": "str1", "value_key": vkey}, "flat": True}


def recognize_dictfold(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the returned-`sdict` dict-fold (census §3).

    Returns {subject, extra_params, acc, gkey, tag, key_key, value} when the IR
    body is *exactly* `out = {}; for x in <listparam>: … out[x.get(K)] = <v> …;
    return out` with ≥1 `out.update(self(…))` merge; else None. Never raises."""
    try:
        return _recognize_dictfold(func)
    except Exception:
        return None


def _recognize_dictfold(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if func.get("return_annotation") != "dict":
        return None
    params = func.get("formal_params", [])
    if not params:
        return None
    body = func.get("body", [])
    if len(body) != 3:
        return None
    init, loop, ret = body

    # init: `<acc> = {}`
    if not (isinstance(init, dict) and init.get("stmt") == "Assign"):
        return None
    acc = init.get("target")
    if not isinstance(acc, str):
        return None
    iv = init.get("value", {})
    if not (isinstance(iv, dict) and iv.get("type") == "DictLit"
            and not iv.get("keys") and not iv.get("values")):
        return None

    # ret: `return <acc>`
    if not (isinstance(ret, dict) and ret.get("stmt") == "Return"
            and _is_var(ret.get("value"), acc)):
        return None

    # loop: `for <x> in <subjparam>:` over a `list`-annotated formal param.
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"):
        return None
    subj = loop.get("iter", {})
    if not (_is_var(subj) and subj.get("name") in params):
        return None
    subj = subj["name"]
    if func.get("param_annotations", {}).get(subj) != "list":
        return None
    x = loop.get("target")
    if not isinstance(x, str):
        return None
    # extra params: every non-subject formal must be a threaded read-only `set`.
    extra = [p for p in params if p != subj]
    pa = func.get("param_annotations", {})
    for e in extra:
        if pa.get(e) != "set":
            return None

    lbody = loop.get("body", [])

    # exactly one ArraySet on <acc> (the runtime-keyed insert).
    sets = [s for s in _iter_dict_nodes(lbody)
            if s.get("stmt") == "ArraySet" and _is_var(s.get("array"), acc)]
    if len(sets) != 1:
        return None
    aset = sets[0]

    # ---- FLAT string-value collector (census §3, flat twin): the shape
    #      `<acc>[<x>["<kkey>"]] = <vloc>` under a `if <vloc>:` truthiness guard,
    #      with `<vloc> = <x>.get("<vkey>")` (NO-DEFAULT get, string value). No
    #      self-merge, no stmt-tag guard, no threaded set. The inline-subscript
    #      KEY (`<x>["<kkey>"]`, not a pre-assigned `.get` local) discriminates
    #      it from the recursive dict-fold below.
    #      (`_build_method_return_annotation_map`.) ----
    _ik = _match_subscript_str(aset.get("index", {}), x)
    if _ik is not None:
        return _recognize_flat_strdictfold(func, subj, acc, x, _ik, aset, lbody)

    # ≥1 self-recursion merge `<acc>.update(self(…))`.
    if not any(_match_acc_update_self(s, acc, func["name"])
               for s in _iter_dict_nodes(lbody)):
        return None

    # KEY: `<acc>[<kv>] = …` where `<kv> = <x>.get("<key_key>"[, def])`.
    idx = aset.get("index", {})
    if not _is_var(idx):
        return None
    kv = idx["name"]
    key_key = None
    for s in _iter_dict_nodes(lbody):
        if (s.get("stmt") == "Assign" and s.get("target") == kv):
            key_key = _match_get_call(s.get("value", {}), x)
            break
    if key_key is None:
        return None

    # tag guard: `<x>.get("<gkey>") == "<TAG>"` somewhere in the loop body.
    gkey = None
    tag = None
    for s in _iter_dict_nodes(lbody):
        if s.get("stmt") == "If":
            t = _match_stmt_tag_test(s.get("test", {}), x)
            if t is not None:
                gkey, tag = "stmt", t
                break
    if tag is None:
        return None

    # VALUE model, keyed on the accumulator's inferred dict value type.
    vtype = (func.get("dict_value_types") or {}).get(acc)
    vexpr = aset.get("value", {})
    value: Dict[str, Any]
    if vtype == "string":
        # `<vloc>.get("<vkey>"[, def])` with `<vloc> = <x>.get("<vckey>"[, def])`.
        if not (isinstance(vexpr, dict) and vexpr.get("type") == "Call"):
            return None
        vfunc = vexpr.get("func", "")
        if not (isinstance(vfunc, str) and vfunc.endswith(".get")):
            return None
        vloc = vfunc[:-len(".get")]
        vkey = _is_string((vexpr.get("args") or [None])[0])
        if vkey is None:
            return None
        vckey = None
        for s in _iter_dict_nodes(lbody):
            if s.get("stmt") == "Assign" and s.get("target") == vloc:
                vckey = _match_get_call(s.get("value", {}), x)
                break
        if vckey is None:
            return None
        # a faithful membership gate needs exactly one threaded set parameter.
        if len(extra) != 1:
            return None
        value = {"kind": "str2", "child_key": vckey, "field_key": vkey,
                 "set_param": extra[0]}
    else:
        # computed / int value → placeholder `PInt 0` (value-refinement).
        value = {"kind": "int"}

    return {"subject": subj, "extra_params": extra, "acc": acc,
            "guard_key": gkey, "tag": tag, "key_key": key_key, "value": value}


def _pv_reader_lines(n: str, key: str) -> List[str]:
    """Emit a spine reader `pydict -> option pyval` for a literal `key` (interned
    constructor for a named key, else the `K_dyn s` `pystr_eq` fallback)."""
    suf = _reader_suffix(key)
    out = [f"  let rec {n}__get_{suf} (d: pydict) : option pyval",
           "    variant { d }",
           "  = match d with",
           "    | DNil -> None"]
    if key in _NAMED_KEYS:
        out.append(f"    | DCons {_NAMED_KEYS[key]} v _ -> Some v")
        out.append(f"    | DCons _ _ rest -> {n}__get_{suf} rest")
    else:
        out.append(f'    | DCons (K_dyn s) v rest -> if pystr_eq s "{key}" then Some v else {n}__get_{suf} rest')
        out.append(f"    | DCons _ _ rest -> {n}__get_{suf} rest")
    out.append("    end")
    return out


def emit_dictfold_group(func: Dict[str, Any], df: Dict[str, Any],
                        whyml_ident) -> List[str]:
    """Emit the returned-`sdict` dict-fold group for a recognized census-§3 fold.

    Functional (`assigns \\nothing`; no `writes`): `build`/`build_val`/
    `build_dict` each return `sdict`, combined by the purely-defined `sappend`.
    Threaded read-only `set` params are typed `map string bool`. Congruent
    (modulo names / sdict-for-set) to the proven `v2_setfold_spike`."""
    n = whyml_ident(func["name"])
    subj = whyml_ident(df["subject"])
    extra = df["extra_params"]
    gkey, tag, kkey = df["guard_key"], df["tag"], df["key_key"]
    value = df["value"]

    extra_sig = "".join(f" ({whyml_ident(e)}: map string bool)" for e in extra)
    extra_args = "".join(f" {whyml_ident(e)}" for e in extra)
    out: List[str] = []

    # ---- spine readers (dedup by key) ----
    needed = ([kkey] if gkey is None else [gkey, kkey])
    if value["kind"] == "str2":
        needed += [value["child_key"], value["field_key"]]
    elif value["kind"] == "str1":
        needed += [value["value_key"]]
    seen: set = set()
    for key in needed:
        if key in seen:
            continue
        seen.add(key)
        out += _pv_reader_lines(n, key)

    ksuf = _reader_suffix(kkey)

    # ---- the per-node pre-action: guarded runtime-keyed insert ----
    out.append(f"  let {n}__pre (d: pydict){extra_sig} : sdict")
    if tag is None:
        # FLAT string-value collector: no stmt-tag guard. Insert `SCons k (PStr v)`
        # iff the KEY reads `Some (PStr k)` AND the no-default `.get` value reads
        # `Some (PStr v)` (the `if v:` truthiness gate; empty-string refinement is
        # a value fact the `ensures True` contract does not need).
        vsuf = _reader_suffix(value["value_key"])
        out.append(f"  = match {n}__get_{ksuf} d with")
        out.append("    | Some (PStr k) ->")
        out.append(f"        (match {n}__get_{vsuf} d with")
        out.append("         | Some (PStr v) -> SCons k (PStr v) SNil")
        out.append("         | _ -> SNil end)")
        out.append("    | _ -> SNil end")
    else:
        gsuf = _reader_suffix(gkey)
        out.append(f"  = match {n}__get_{gsuf} d with")
        out.append("    | Some (PStr s) ->")
        out.append(f'        if pystr_eq s "{tag}" then')
        out.append(f"          (match {n}__get_{ksuf} d with")
        out.append("           | Some (PStr k) ->")
        if value["kind"] == "str2":
            csuf = _reader_suffix(value["child_key"])
            fsuf = _reader_suffix(value["field_key"])
            setp = whyml_ident(value["set_param"])
            out.append(f"               (match {n}__get_{csuf} d with")
            out.append("                | Some (PDict vd) ->")
            out.append(f"                    (match {n}__get_{fsuf} vd with")
            out.append(f"                     | Some (PStr fn) -> if Map.get {setp} fn then SCons k (PStr fn) SNil else SNil")
            out.append("                     | _ -> SNil end)")
            out.append("                | _ -> SNil end)")
        else:
            out.append("               SCons k (PInt 0) SNil")
        out.append("           | _ -> SNil end)")
        out.append("        else SNil")
        out.append("    | _ -> SNil end")

    # ---- the returned-sdict walk / build_val / build_dict group ----
    out.append(f"  let rec {n} ({subj}: list pyval){extra_sig} : sdict")
    out.append("    requires { true } ensures { true }")
    out.append(f"    variant {{ size_list {subj} }}")
    out.append(f"  = match {subj} with")
    out.append("    | Nil -> SNil")
    out.append(f"    | Cons h t -> sappend ({n}__val h{extra_args}) ({n} t{extra_args})")
    out.append("    end")
    out.append(f"  with {n}__val (v: pyval){extra_sig} : sdict")
    out.append("    requires { true } ensures { true }")
    out.append("    variant { pv_size v }")
    out.append("  = match v with")
    out.append(f"    | PDict d -> sappend ({n}__pre d{extra_args}) ({n}__dict d{extra_args})")
    out.append(f"    | PList xs -> {n} xs{extra_args}")
    out.append("    | _ -> SNil")
    out.append("    end")
    out.append(f"  with {n}__dict (d: pydict){extra_sig} : sdict")
    out.append("    requires { true } ensures { true }")
    out.append("    variant { size_dict d }")
    out.append("  = match d with")
    out.append("    | DNil -> SNil")
    out.append(f"    | DCons _ v rest -> sappend ({n}__val v{extra_args}) ({n}__dict rest{extra_args})")
    out.append("    end")
    return out


# =========================================================================
# G-void-dispatch-thin — the thin VOID-returning statement-list fan-out:
#     def wrapper(stmts, *ctx):
#         for s in stmts:
#             if isinstance(s, dict):
#                 sibling(s, *ctx)
# `sibling` is a DIFFERENT top-level function that STAYS \trusted: its `val`
# types every untyped/Any param with the corpus-wide opaque-`int` fallback
# (`_param_type_str`'s final default — no annotation, no other recognized
# shape). To keep the call `sibling h ...` type-matching that unchanged
# `val` with NO callee edit and NO new value model, the wrapper's own
# `stmts: List[...]` parameter is modelled — UNLIKE the standard `array`
# lowering — as the built-in Why3 `list int` (Cons/Nil): an OPAQUE-element
# linked list, so each element `s` is ALSO plain `int`.
#
# This sidesteps the array-for-loop invariant problem entirely: a plain
# (non-`@mutable_state`) `for x in <list>:` lowers to an index/`while` loop
# whose termination needs an explicit `#@ loop variant` naming the internal
# `_idx_x` counter — a name Module4 does not expose to source-level
# annotations, and the body text must stay verbatim-faithful to the live
# source (no annotation can be inserted). Structural `Cons h t -> …;
# wrapper t …` recursion instead terminates for FREE off `list`'s own
# well-founded order (`variant { stmts }`, Why3-native — no bespoke size
# theory, matching the plan's "reuse existing termination machinery, don't
# add a new theory").
#
# `isinstance(s, dict)` on the opaque `s` lowers exactly as the standard
# (non-recognized) `_handle_isinstance` does for an untyped/Any value in
# program (non-spec) context: an UNINTERPRETED `typeof_op` tag read compared
# against the inlined `tag_dict` literal (4) — the SAME formula
# (`sum(ord(c) for c in name)`) and the SAME literal `_handle_isinstance`
# uses, so the guard is neither constant-folded true nor false, faithfully
# preserving "s's dynamic type is unknown here" rather than erasing the
# branch. `ensures True` makes the branch's actual outcome irrelevant to
# the wrapper's own proof.
#
# ONE code path handles every match (no per-method name/tag is hardcoded):
# the sibling's name+arity and the ctx params are read off the recognized
# call itself.
# =========================================================================

def recognize_void_dispatch(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the G-void-dispatch-thin fan-out (see the module
    note above): a void function whose ENTIRE body is `for s in stmts: if
    isinstance(s, dict): <sibling>(s, *ctx)`, where `<sibling>` is any OTHER
    top-level function (not `func` itself, not a `self.`/dotted call) and
    `ctx` is `func`'s remaining formal params, forwarded positionally and
    unchanged. `stmts` (must be `list`-annotated) and the sibling name/arity
    are the recognizer's only degrees of freedom.

    Returns {subject, stmtvar, callee, ctx_params} or None. Never raises."""
    try:
        return _recognize_void_dispatch(func)
    except Exception:
        return None


def _recognize_void_dispatch(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) < 2:
        return None
    subj, ctx_params = params[0], params[1:]
    pann = func.get("param_annotations", {}) or {}
    if pann.get(subj) != "list":
        return None
    # ctx params stay fully opaque (no OTHER recognized annotation) — the
    # thing that lets them lower to the same `int` fallback the unmodified
    # \trusted sibling's `val` already uses.
    if any(p in pann for p in ctx_params):
        return None
    if func.get("return_annotation") not in ("None", None):
        return None
    body = func.get("body", [])
    if len(body) != 1:
        return None
    loop = body[0]
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"
            and not loop.get("orelse") and _is_var(loop.get("iter"), subj)):
        return None
    stmtvar = loop.get("target")
    if not isinstance(stmtvar, str) or stmtvar in ctx_params or stmtvar == subj:
        return None
    lbody = loop.get("body", [])
    if len(lbody) != 1:
        return None
    guard = lbody[0]
    if not (isinstance(guard, dict) and guard.get("stmt") == "If" and not guard.get("orelse")):
        return None
    if not _match_isinstance(guard.get("test", {}), stmtvar, "dict"):
        return None
    gbody = guard.get("body", [])
    if len(gbody) != 1:
        return None
    call_stmt = gbody[0]
    if not (isinstance(call_stmt, dict) and call_stmt.get("stmt") == "Expr"):
        return None
    call = call_stmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return None
    callee = call.get("func")
    # a DIFFERENT top-level function — not self-recursion, not a method call
    # (a dotted `self.foo`/`obj.foo` callee is a different call-lowering
    # shape entirely, out of scope for this recognizer).
    if not isinstance(callee, str) or "." in callee or callee == func.get("name"):
        return None
    args = call.get("args", [])
    if len(args) != 1 + len(ctx_params):
        return None
    if not _is_var(args[0], stmtvar):
        return None
    for a, p in zip(args[1:], ctx_params):
        if not _is_var(a, p):
            return None
    return {"subject": subj, "stmtvar": stmtvar, "callee": callee,
            "ctx_params": ctx_params}


def emit_void_dispatch_group(func: Dict[str, Any], desc: Dict[str, Any],
                             whyml_ident) -> List[str]:
    """Emit the G-void-dispatch-thin fan-out as structural `list int`
    recursion (see the module note above for the type-matching rationale).
    The callee is called UNCHANGED (still `\\trusted`; its `val` keeps the
    standard opaque-`int` param types) — the wrapper's own element/ctx types
    are chosen to match it exactly, so no callee-side edit is needed.

    The `isinstance(s, dict)` guard is lowered to `mod h 2 = 0` — an
    UNDECIDABLE-to-the-solver condition over the already-in-scope, otherwise
    unconstrained `h` (the Cons head), using ONLY `int.EuclideanDivision`
    (unconditionally `use`d by every emitted module already). This was
    chosen over registering a NEW abstract `typeof_op` symbol (the standard
    `_handle_isinstance` opaque fallback): measured empirically, adding that
    symbol to this file's shared module pushed the PRE-EXISTING, already
    near-timeout `wf_ir_binds` lemma (`_emit_pydict_theory`, unrelated to
    this recognizer) from Valid to Timeout — a whole-file regression with
    zero new declarations avoids. `ensures True` makes the branch's actual
    outcome irrelevant either way; `mod` keeps the guard genuinely opaque
    (not constant-folded) without perturbing the shared proof context."""
    n = whyml_ident(func["name"])
    callee = whyml_ident(desc["callee"])
    ctx = [whyml_ident(p) for p in desc["ctx_params"]]
    ctx_sig = "".join(f" ({c}: int)" for c in ctx)
    ctx_args = "".join(f" {c}" for c in ctx)
    h = whyml_ident(desc["stmtvar"])
    out: List[str] = []
    out.append(f"  let rec {n} (stmts: list int){ctx_sig} : unit")
    out.append("    requires { true } ensures { true }")
    out.append("    variant { stmts }")
    out.append("  = match stmts with")
    out.append("    | Nil -> ()")
    out.append(f"    | Cons {h} t ->")
    out.append(f"        (if (mod {h} 2 = 0) then {callee} {h}{ctx_args} else ());")
    out.append(f"        {n} t{ctx_args}")
    out.append("    end")
    return out


# =========================================================================
# G-void-generic-descend — the VOID untyped-value tree descender (the
# `_pb_descend`/`_cs_descend` twin pair, mutually recursive with the
# G-void-dispatch-thin siblings `_pb_body`/`_cs_body`):
#     def wrapper(v, *ctx):
#         if isinstance(v, dict):
#             if "stmt" in v:
#                 sibling(v, *ctx)
#             else:
#                 for x in v.values():
#                     wrapper(x, *ctx)
#         elif isinstance(v, list):
#             for x in v:
#                 wrapper(x, *ctx)
#
# UNLIKE G-void-dispatch-thin, the subject `v` is genuinely heterogeneous
# (no `List[...]` annotation — it is descended through both `dict` and
# `list` shapes across the recursion), so it needs the REAL `pyval`/`pydict`
# L1 catamorphism (`needs_pydict`, the `recognize_bool_existence` theory) —
# not the opaque `list int` model. `isinstance(v, dict)`/`isinstance(v,
# list)` lower to the pyval tag match itself (`PDict`/`PList`), which is
# MORE faithful than the `mod h 2 = 0` opaque-guard fallback (real
# information, not a scrambled parity bit) — that fallback is reserved for
# an already-opaque scalar, which `v` here is not. `"stmt" in v` reuses the
# EXISTING `_emit_stmt_reader` presence reader verbatim (the same helper
# `recognize_bool_existence`'s group already emits) — no new WhyML theory.
#
# `sibling` (`_pb_stmt`/`_cs_stmt`) STAYS \trusted, so its `val` keeps the
# corpus-wide opaque-`int` param type for its untyped `s` (the
# `_param_type_str` Any-fallback) — the SAME convention `_pb_body`'s already-
# landed `emit_void_dispatch_group` relies on. Since a `\trusted val` has no
# body, its contract (`ensures true`) makes the caller-supplied int value
# formally irrelevant; the call forwards the literal `0` as that opaque
# handle (`pv_size`/`size_dict` are pure LOGIC `function`s — ghost/spec-only,
# rejected in a program-expression position, so they cannot supply it) —
# sound for the same reason `emit_void_dispatch_group` forwards an opaque
# `list int` Cons element with no relation to real dict content: the
# trusted callee cannot observe or constrain the value it receives.
#
# Termination is the direct structural sub-term at every recursive site
# (`pv_size v` / `size_dict d` / `size_list xs`), split_vc-robust — the
# proven A-bool/A-set shape reused verbatim.
#
# ONE code path handles every match (no per-method name/tag is hardcoded):
# the sibling's name and the ctx params are read off the recognized call.
# =========================================================================

def recognize_void_generic_descend(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the G-void-generic-descend untyped tree
    descender (see the module note above): a void function whose ENTIRE
    body is `if isinstance(v, dict): (if "stmt" in v: sibling(v, *ctx) else:
    for x in v.values(): self(x, *ctx)) elif isinstance(v, list): for x in
    v: self(x, *ctx)`. `sibling` is any OTHER top-level function (not
    `func` itself, not a dotted call); `ctx` is `func`'s remaining formal
    params, forwarded positionally and unchanged. `v` must be UNANNOTATED
    (the genuinely heterogeneous subject — a `list`-annotated subject is the
    G-void-dispatch-thin shape instead).

    Returns {subject, ctx_params, callee} or None. Never raises."""
    try:
        return _recognize_void_generic_descend(func)
    except Exception:
        return None


def _match_self_recurse_call(body: Any, self_name: str, xvar: str,
                             ctx_params: List[str]) -> bool:
    """`self(<xvar>, *ctx_params)` as the sole statement of a loop body."""
    if not isinstance(body, list) or len(body) != 1:
        return False
    s = body[0]
    if not (isinstance(s, dict) and s.get("stmt") == "Expr"):
        return False
    call = s.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"
            and call.get("func") == self_name):
        return False
    args = call.get("args", [])
    if len(args) != 1 + len(ctx_params):
        return False
    if not _is_var(args[0], xvar):
        return False
    for a, p in zip(args[1:], ctx_params):
        if not _is_var(a, p):
            return False
    return True


def _recognize_void_generic_descend(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) < 2:
        return None
    subj, ctx_params = params[0], params[1:]
    pann = func.get("param_annotations", {}) or {}
    # `v` must be genuinely untyped — a `list`-annotated subject is the
    # G-void-dispatch-thin shape (`recognize_void_dispatch`), a different
    # recognizer.
    if subj in pann or any(p in pann for p in ctx_params):
        return None
    if func.get("return_annotation") not in ("None", None):
        return None
    body = func.get("body", [])
    if len(body) != 1:
        return None
    outer = body[0]
    if not (isinstance(outer, dict) and outer.get("stmt") == "If"):
        return None
    if not _match_isinstance(outer.get("test", {}), subj, "dict"):
        return None
    obody = outer.get("body", [])
    if len(obody) != 1:
        return None
    inner = obody[0]
    if not (isinstance(inner, dict) and inner.get("stmt") == "If"):
        return None
    itest = inner.get("test", {})
    if not (isinstance(itest, dict) and itest.get("type") == "BinOp"
            and itest.get("op") == "in"
            and _is_string(itest.get("left")) == "stmt"
            and _is_var(itest.get("right"), subj)):
        return None
    # true arm: sibling(v, *ctx)
    ibody = inner.get("body", [])
    if len(ibody) != 1:
        return None
    call_stmt = ibody[0]
    if not (isinstance(call_stmt, dict) and call_stmt.get("stmt") == "Expr"):
        return None
    call = call_stmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return None
    callee = call.get("func")
    if not isinstance(callee, str) or "." in callee or callee == func.get("name"):
        return None
    cargs = call.get("args", [])
    if len(cargs) != 1 + len(ctx_params):
        return None
    if not _is_var(cargs[0], subj):
        return None
    for a, p in zip(cargs[1:], ctx_params):
        if not _is_var(a, p):
            return None
    # false arm: for x in v.values(): self(x, *ctx)
    iorelse = inner.get("orelse", [])
    if len(iorelse) != 1:
        return None
    dloop = iorelse[0]
    if not (isinstance(dloop, dict) and dloop.get("stmt") == "For"
            and not dloop.get("orelse")):
        return None
    dit = dloop.get("iter", {})
    if not (isinstance(dit, dict) and dit.get("type") == "Call"
            and dit.get("func") == f"{subj}.values" and not dit.get("args")):
        return None
    xvar = dloop.get("target")
    if not isinstance(xvar, str) or xvar in ctx_params or xvar == subj:
        return None
    if not _match_self_recurse_call(dloop.get("body", []), func.get("name"),
                                    xvar, ctx_params):
        return None
    # outer orelse: elif isinstance(v, list): for x in v: self(x, *ctx)
    oorelse = outer.get("orelse", [])
    if len(oorelse) != 1:
        return None
    linner = oorelse[0]
    if not (isinstance(linner, dict) and linner.get("stmt") == "If"
            and not linner.get("orelse")):
        return None
    if not _match_isinstance(linner.get("test", {}), subj, "list"):
        return None
    lbody = linner.get("body", [])
    if len(lbody) != 1:
        return None
    lloop = lbody[0]
    if not (isinstance(lloop, dict) and lloop.get("stmt") == "For"
            and not lloop.get("orelse")):
        return None
    if not _is_var(lloop.get("iter"), subj):
        return None
    xvar2 = lloop.get("target")
    if not isinstance(xvar2, str) or xvar2 in ctx_params or xvar2 == subj:
        return None
    if not _match_self_recurse_call(lloop.get("body", []), func.get("name"),
                                    xvar2, ctx_params):
        return None
    return {"subject": subj, "ctx_params": ctx_params, "callee": callee}


def emit_void_generic_descend_group(func: Dict[str, Any], desc: Dict[str, Any],
                                    whyml_ident) -> List[str]:
    """Emit the G-void-generic-descend untyped tree descender as a `pyval`/
    `pydict`/`list pyval` mutual catamorphism into `unit` (see the module
    note above). Reuses `_emit_stmt_reader` verbatim for the `"stmt" in v`
    presence check (only its `__get_stmt` half is consulted here; the
    `__stmt_is` half it also emits is simply unused, not a new theory)."""
    n = whyml_ident(func["name"])
    callee = whyml_ident(desc["callee"])
    ctx = [whyml_ident(p) for p in desc["ctx_params"]]
    ctx_sig = "".join(f" ({c}: int)" for c in ctx)
    ctx_args = "".join(f" {c}" for c in ctx)
    out: List[str] = []
    out.extend(_emit_stmt_reader(n))
    out.append(f"  let rec {n} (v: pyval){ctx_sig} : unit")
    out.append("    requires { true } ensures { true }")
    out.append("    variant { pv_size v }")
    out.append("  = match v with")
    out.append(f"    | PDict d -> (match {n}__get_stmt d with")
    out.append(f"        | Some _ -> {callee} 0{ctx_args}")
    out.append(f"        | None -> {n}__d d{ctx_args} end)")
    out.append(f"    | PList xs -> {n}__l xs{ctx_args}")
    out.append("    | _ -> ()")
    out.append("    end")
    out.append(f"  with {n}__d (d: pydict){ctx_sig} : unit")
    out.append("    requires { true } ensures { true }")
    out.append("    variant { size_dict d }")
    out.append("  = match d with DNil -> ()")
    out.append(f"    | DCons _ v rest -> {n} v{ctx_args}; {n}__d rest{ctx_args} end")
    out.append(f"  with {n}__l (xs: list pyval){ctx_sig} : unit")
    out.append("    requires { true } ensures { true }")
    out.append("    variant { size_list xs }")
    out.append("  = match xs with Nil -> ()")
    out.append(f"    | Cons h t -> {n} h{ctx_args}; {n}__l t{ctx_args} end")
    return out


# =========================================================================
# stmt_ir tree-walk existence recogniser — `recognize_stmt_has`.
#
# tree-walk-wall-impl.md (self-tcb-reduction, GATE-S PROVEN): the FAITHFUL,
# TYPED counterpart of `recognize_bool_existence` (which folds over the
# dynamic `pyval` ADT). This recognises the `_body_has_return`-shaped
# statement-tree existence walk — a flat direct-recursive
#   `for stmt in body:
#        if stmt.get("stmt") == "<TAG>": return True
#        <descend into stmt's statement-body child lists via self-recursion>
#    return False`
# — and emits the CERTIFIED stmt_ir catamorphism `stmt_has`/`sl_has`/`hl_has`/
# `mcl_has` (verbatim from the full-M5-scale-proven scratchpad/standalone.mlw,
# with the LEXICOGRAPHIC `variant { size_stmt s, 0 }` / `{ size_slist l, 1 }`
# / `{ size_hlist l, 1 }` / `{ size_mclist l, 1 }` — the STRUCTURAL variant
# TIMED OUT on the record-field-projection descents at full scale). The
# recognised discriminant TAG(s) drive which stmt_ir constructor arm(s) return
# `true` (the mutation-sensitive, non-facade signal): "Return" -> SReturn,
# "While" -> SWhile, ... — every other compound constructor STRUCTURALLY
# OR-descends its statement-body children. The body param is typed `stmt_list`
# and the whole function lowers to `<n>__sl_has body`.
#
# NOT a name-keyed facade: the emitted true-arm(s) are DERIVED from the tag
# literal read out of the body's `stmt.get("stmt") == "<TAG>"` test, so
# changing the discriminant in the source moves (or removes) the true-arm and
# the emitted .mlw changes (the emission mutation test).

# leaf (body-less) stmt_ir constructors, by discriminant tag -> match pattern.
_STMT_LEAF_TAG_CTOR = {
    "Pass": "SPass", "Break": "SBreak", "Continue": "SContinue",
    "Return": "SReturn _", "Expr": "SExpr _", "Assign": "SAssign _ _",
    "Assert": "SAssert _ _", "AugAssign": "SAugAssign _ _ _",
    "FieldAugAssign": "SFieldAugAssign _ _ _", "ArraySet": "SArraySet _ _ _",
    "DelSubscript": "SDelSubscript _ _", "FieldAssign": "SFieldAssign _ _ _",
    "ArraySliceSet": "SArraySliceSet _ _ _ _", "TupleUnpack": "STupleUnpack _ _",
    "GhostArraySet": "SGhostArraySet _ _ _", "GhostAssign": "SGhostAssign _ _ _ _",
}

# compound (statement-body-carrying) stmt_ir constructors: (match pattern, tag,
# [(list-kind, bound-var), ...]) — the descent OR-folds each child list with the
# recogniser sibling for that list kind (sl=stmt_list, hl=handler_list,
# mcl=match_case_list). handler_list/match_case_list descend the record's body
# field (h.eh_body / c.mc_body).
_STMT_COMPOUND = [
    ("SWhile _ b", "While", [("sl", "b")]),
    ("SIf _ b o", "If", [("sl", "b"), ("sl", "o")]),
    ("SFor _ b", "For", [("sl", "b")]),
    ("STry b hs oe fb", "Try",
     [("sl", "b"), ("hl", "hs"), ("sl", "oe"), ("sl", "fb")]),
    ("SMatch _ cs", "Match", [("mcl", "cs")]),
    ("SCriticalSection _ b _ _", "CriticalSection", [("sl", "b")]),
]


def _collect_stmt_selfcalls(node: Any, self_name: str, out: List[Any]) -> None:
    """Collect every Call node whose `func` is the bare self name (confirms the
    walk is a genuine self-recursive tree descent, not a flat one-level scan)."""
    if isinstance(node, dict):
        if node.get("type") == "Call" and node.get("func") == self_name:
            out.append(node)
        for v in node.values():
            _collect_stmt_selfcalls(v, self_name, out)
    elif isinstance(node, list):
        for x in node:
            _collect_stmt_selfcalls(x, self_name, out)


def recognize_stmt_has(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the `_body_has_return`-shaped stmt_ir tree-walk
    existence fold. Returns {subject, tags, self_name} or None. Never raises."""
    try:
        return _recognize_stmt_has(func)
    except Exception:
        return None


def _recognize_stmt_has(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    subj = params[0]
    pa = func.get("param_annotations", {}) or {}
    if pa.get(subj) != "list":
        return None
    if func.get("return_annotation") != "bool":
        return None
    body = func.get("body", [])
    if len(body) != 2:
        return None
    loop, tail = body
    # tail: `return False`
    if not (isinstance(tail, dict) and tail.get("stmt") == "Return"
            and isinstance(tail.get("value"), dict)
            and tail["value"].get("type") == "Bool"
            and tail["value"].get("value") is False):
        return None
    # loop: `for stmt in <subj>: <arms>`
    if not (isinstance(loop, dict) and loop.get("stmt") == "For"
            and _is_var(loop.get("iter"), subj)):
        return None
    stmtv = loop.get("target")
    if not isinstance(stmtv, str):
        return None
    lbody = loop.get("body", [])
    if len(lbody) < 2:
        return None
    self_name = func.get("name")
    self_calls: List[Any] = []
    _collect_stmt_selfcalls(lbody, self_name, self_calls)
    if not self_calls:
        return None
    # collect every `if <stmt>.get("stmt") == "<TAG>": return True` discriminant
    tags: List[str] = []
    for a in lbody:
        if not (isinstance(a, dict) and a.get("stmt") == "If"
                and not a.get("orelse")):
            continue
        tg = _match_stmt_tag_test(a.get("test", {}), stmtv)
        if (tg is not None and len(a.get("body", [])) == 1
                and _is_bool_true_return(a["body"][0])):
            tags.append(tg)
    if not tags:
        return None
    _known = set(_STMT_LEAF_TAG_CTOR) | {c[1] for c in _STMT_COMPOUND}
    for t in tags:
        if t not in _known:
            return None
    return {"subject": subj, "tags": tags, "self_name": self_name}


def emit_stmt_has_group(func: Dict[str, Any], desc: Dict[str, Any],
                        whyml_ident) -> List[str]:
    """Emit the certified stmt_ir existence catamorphism for a recognised walk.

    The `stmt_has`/`sl_has`/`hl_has`/`mcl_has` mutual group is verbatim from the
    full-M5-scale-proven scratchpad/standalone.mlw (LEXICOGRAPHIC variant); only
    the true-arm(s) vary with the recognised discriminant tag(s). The whole
    `_body_has_return` lowers to `<n>__sl_has body` over a `stmt_list` param."""
    n = whyml_ident(func["name"])
    tags = set(desc["tags"])
    arms: List[str] = []
    for tag in desc["tags"]:
        if tag in _STMT_LEAF_TAG_CTOR:
            arms.append(f"    | {_STMT_LEAF_TAG_CTOR[tag]} -> true")
    for pat, tag, children in _STMT_COMPOUND:
        if tag in tags:
            arms.append(f"    | {pat} -> true")
        else:
            rhs = " || ".join(f"{n}__{k}_has {v}" for k, v in children)
            arms.append(f"    | {pat} -> {rhs}")
    arms.append("    | _ -> false")
    out: List[str] = []
    out.append(f"  let rec function {n}__stmt_has (s: stmt_ir) : bool")
    out.append("    variant { size_stmt s, 0 }")
    out.append("  = match s with")
    out.extend(arms)
    out.append("    end")
    out.append(f"  with function {n}__sl_has (l: stmt_list) : bool")
    out.append("    variant { size_slist l, 1 }")
    out.append(f"  = match l with SLNil -> false"
               f" | SLCons h t -> {n}__stmt_has h || {n}__sl_has t end")
    out.append(f"  with function {n}__hl_has (l: handler_list) : bool")
    out.append("    variant { size_hlist l, 1 }")
    out.append(f"  = match l with HLNil -> false"
               f" | HLCons h t -> {n}__sl_has h.eh_body || {n}__hl_has t end")
    out.append(f"  with function {n}__mcl_has (l: match_case_list) : bool")
    out.append("    variant { size_mclist l, 1 }")
    out.append(f"  = match l with MCNil -> false"
               f" | MCCons c t -> {n}__sl_has c.mc_body || {n}__mcl_has t end")
    out.append(f"  let function {n} (body: stmt_list) : bool")
    out.append("    requires { true } ensures { true }")
    out.append(f"  = {n}__sl_has body")
    return out


# =========================================================================
# IRScanner `obj: Any` TYPE-existence fold — recognize_type_existence.
#
# genexp-erasure-wall / wall-lessons (l), R2d+R3 convergence: the generic-`Any`
# tree existence predicate rooted at a SCALAR untyped `obj` with a dict-first
# `isinstance` dispatch, a `.get("type") == "<TAG>"` discriminant, and mutual
# recursion via `any(self(v) for v in obj.values())` / `any(self(x) for x in
# obj)`:
#
#     def uses_string(obj):
#         if isinstance(obj, dict):
#             if obj.get("type") == "String": return True
#             return any(IRScanner.uses_string(v) for v in obj.values())
#         if isinstance(obj, list):
#             return any(IRScanner.uses_string(item) for item in obj)
#         return False
#
# Before this, BOTH the `obj: Any` int-erasure AND the `any(genexp)` unconstrained
# oracle collapsed the emitted body to a value that never mentions `obj`
# (`typeof_op 315`, `obj_get_1 <hash>`, `any_1 (Array.make 1 0)`) — a fully
# vacuous facade the mutation test cannot see (wall-lessons (l),
# bin/check-emitted-vacuity.py). This emits the certified pyval/pydict/list-pyval
# catamorphism (the SAME proven L1 theory as recognize_bool_existence /
# recognize_void_generic_descend — no new ADT, no new certificate, ledger 3),
# scalar-rooted and keyed on the interned "type" key (K_type). The `let rec ...
# with ... variant { pv_size obj } / { size_dict d } / { size_list xs }` weaving
# is the R2d rec-group fold: the fold co-lives with the recursive predicate in
# ONE mutual group, so the self-recursion binds (no `unbound symbol`) and
# terminates on the structural pyval measure. The emitted body matches on `obj`
# (de-vacuified) and the recognised discriminant tag drives the true-arm (the
# mutation-sensitive, non-facade signal). Fail-closed: a body-fidelity bug yields
# a loud unprovable instance, never a false proof. The family: uses_string /
# uses_subscript / uses_sum / uses_set_card (single "type"-tag shape).


def _match_type_tag_test(test: Any, subj: str) -> Optional[Tuple[str, str]]:
    """`<subj>.get("<key>") == "<TAG>"` -> (key, TAG); None (fail-closed)."""
    if not (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "=="):
        return None
    left, right = test.get("left", {}), test.get("right", {})
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == f"{subj}.get"):
        return None
    gargs = left.get("args", [])
    if len(gargs) != 1:
        return None
    key = _is_string(gargs[0])
    tag = _is_string(right)
    if key is None or tag is None:
        return None
    return (key, tag)


def _flatten_and(test: Any) -> List[Any]:
    """Flatten a left/right-nested `and` chain into its leaf conjuncts."""
    if (isinstance(test, dict) and test.get("type") == "BinOp"
            and test.get("op") == "and"):
        return (_flatten_and(test.get("left", {}))
                + _flatten_and(test.get("right", {})))
    return [test]


def _match_key_in_tuple(node: Any, subj: str) -> Optional[Tuple[str, List[str]]]:
    """`<subj>.get("<key>") in ("<t0>", "<t1>", ...)` -> (key, [tags])."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "in"):
        return None
    left, right = node.get("left", {}), node.get("right", {})
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == f"{subj}.get"):
        return None
    gargs = left.get("args", [])
    if len(gargs) != 1:
        return None
    key = _is_string(gargs[0])
    if key is None:
        return None
    if not (isinstance(right, dict) and right.get("type") == "Tuple"):
        return None
    tags = [_is_string(e) for e in right.get("elts", [])]
    if not tags or any(t is None for t in tags):
        return None
    return (key, tags)


def _match_type_discriminant(test: Any, subj: str,
                             carried: Optional[List[str]] = None
                             ) -> Optional[Dict[str, Any]]:
    """The tag-arm discriminant of an IRScanner type-existence predicate.

    Shapes recognised, all keyed on the interned "type" key:
      * SIMPLE   `<subj>.get("type") == "<TAG>"`
        -> {kind: "simple", tag: TAG}
      * COMPOUND `<subj>.get("type") == "<T>" and <subj>.get("<k2>") in (<tags>)
                  [and <extra conjuncts>]`  (`uses_ord_chr`/`uses_minmax`)
        -> {kind: "compound", type_tag: T, key2: k2 ("func"/"op"), tags: [...]}
      * PARAM    `<subj>.get("type") == "<T>" and <subj>.get("<k2>") == <carried>`
                 (`is_recursive`: `type=="Call" and func==name`)
        -> {kind: "param", type_tag: T, key2: k2 ("func"/"op"), param: <name>}
        the RHS is a `Var` naming one of the `carried` scalar params — the
        discriminant compares against a runtime string value, not a literal.
        `k2` is restricted to the interned named keys func/op. Any EXTRA
        conjuncts (`uses_minmax`'s `len(obj.get("args",[]))==2`) are DROPPED —
        a sound over-approximation under the fixed `ensures True` contract
        (insight C, the same doctrine `recognize_bool_existence` uses to drop
        its membership-set conjunct): the emitted catamorphism matches a
        SUPERSET of the source's true-set, so nothing false is derived, and the
        mutation-sensitive `type`/`k2`-tag discriminants (the non-facade signal)
        are preserved verbatim.
    """
    carried = carried or []
    # SIMPLE
    kt = _match_type_tag_test(test, subj)
    if kt is not None and kt[0] == "type":
        return {"kind": "simple", "tag": kt[1]}
    conjs = _flatten_and(test)
    if len(conjs) < 2:
        return None
    # NESTED: any conjunct is a child-field type projection
    # `<subj>["<nk>"].get("<sk>") == "<TAG>"` (`uses_array_lit`'s `[0]*n` arm:
    # `type=="BinOp" and op=="*" and obj["left"].get("type")=="ArrayLit"`).
    # Collect a general AND-fact list; drop the `isinstance(obj.get("left"),dict)`
    # guard as a sound over-approximation (the pyval `type_is` on the child already
    # returns false for a non-PDict child, so the guard is subsumed).
    if any(_match_nested_type_proj(c, subj) is not None for c in conjs):
        n_type_tag = None
        facts: List[Dict[str, Any]] = []
        for c in conjs:
            st = _match_type_tag_test(c, subj)
            if st is not None and st[0] == "type":
                if n_type_tag is not None:
                    return None
                n_type_tag = st[1]
                continue
            if st is not None and st[0] in ("func", "op"):
                facts.append({"t": "keylit", "key": st[0], "tag": st[1]})
                continue
            kin = _match_key_in_tuple(c, subj)
            if kin is not None and kin[0] in ("func", "op"):
                facts.append({"t": "keyin", "key": kin[0], "tags": kin[1]})
                continue
            kep = _match_key_eq_param(c, subj, carried)
            if kep is not None and kep[0] in ("func", "op"):
                facts.append({"t": "keyparam", "key": kep[0], "param": kep[1]})
                continue
            pr = _match_nested_type_proj(c, subj)
            if pr is not None:
                facts.append({"t": "proj", "key": pr[0], "subkey": pr[1],
                              "tag": pr[2]})
                continue
            # droppable extra (the isinstance guard) — insight-C over-approx.
        if n_type_tag is None or not facts:
            return None
        return {"kind": "nested", "type_tag": n_type_tag, "facts": facts}
    # COMPOUND / PARAM: require exactly one `type==T` conjunct and exactly one
    # secondary key conjunct (either `k2 in (tags)` or `k2 == <carried>`) over an
    # interned named key.
    type_tag = None
    key2 = None
    tags: List[str] = []
    param = None
    for c in conjs:
        st = _match_type_tag_test(c, subj)
        if st is not None and st[0] == "type":
            if type_tag is not None:
                return None
            type_tag = st[1]
            continue
        kin = _match_key_in_tuple(c, subj)
        if kin is not None and kin[0] in ("func", "op"):
            if key2 is not None:
                return None
            key2, tags = kin
            continue
        kep = _match_key_eq_param(c, subj, carried)
        if kep is not None and kep[0] in ("func", "op"):
            if key2 is not None:
                return None
            key2, param = kep
            continue
        # any other conjunct is an insight-C droppable extra — leave it be.
    if type_tag is None or key2 is None:
        return None
    if param is not None:
        return {"kind": "param", "type_tag": type_tag, "key2": key2,
                "param": param}
    return {"kind": "compound", "type_tag": type_tag, "key2": key2, "tags": tags}


def _match_key_eq_param(node: Any, subj: str, carried: List[str]
                        ) -> Optional[Tuple[str, str]]:
    """`<subj>.get("<key>") == <Var carried_i>` -> (key, carried_i); None.
    The RHS must be a bare `Var` naming one of the carried scalar params."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "=="):
        return None
    left, right = node.get("left", {}), node.get("right", {})
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == f"{subj}.get"):
        return None
    gargs = left.get("args", [])
    if len(gargs) != 1:
        return None
    key = _is_string(gargs[0])
    if key is None:
        return None
    if not (isinstance(right, dict) and right.get("type") == "Var"
            and right.get("name") in carried):
        return None
    return (key, right["name"])


def _match_nested_type_proj(node: Any, subj: str
                            ) -> Optional[Tuple[str, str, str]]:
    """`<subj>["<nkey>"].get("<subkey>") == "<TAG>"` -> (nkey, subkey, TAG); None.

    Module5 lowers `obj["left"].get("type")` to a `Call func="get"` whose
    `receiver` is the `Subscript(<subj>, "<nkey>")` and whose single arg is the
    string subkey. A child-field type projection (`uses_array_lit`)."""
    if not (isinstance(node, dict) and node.get("type") == "BinOp"
            and node.get("op") == "=="):
        return None
    left, right = node.get("left", {}), node.get("right", {})
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == "get"):
        return None
    recv = left.get("receiver")
    if not (isinstance(recv, dict) and recv.get("type") == "Subscript"
            and _is_var(recv.get("value"), subj)):
        return None
    nkey = _is_string(recv.get("index"))
    gargs = left.get("args", [])
    if len(gargs) != 1:
        return None
    subkey = _is_string(gargs[0])
    tag = _is_string(right)
    if nkey is None or subkey is None or tag is None:
        return None
    return (nkey, subkey, tag)


def _match_any_selfrecurse_genexp(node: Any, subj: str, self_base: str,
                                  iter_ok, carried: Optional[List[str]] = None
                                  ) -> bool:
    """`any(<self>(<carried...>, <lv>) for <lv> in <iter>)` — a bare-`any` over a
    filter-less single-generator comprehension whose element is a SELF call
    (basename `self_base`) whose LAST arg is the bound variable, preceded by the
    `carried` scalar params (as `Var`s, in order), and whose iterable satisfies
    `iter_ok(iter_node, lv)`. `carried=None`/`[]` is the plain `self(lv)` shape."""
    carried = carried or []
    if not (isinstance(node, dict) and node.get("type") == "Call"
            and node.get("func") == "any"):
        return False
    args = node.get("args", [])
    if len(args) != 1:
        return False
    ge = args[0]
    if not (isinstance(ge, dict) and ge.get("type") in ("GenExp", "ListComp")):
        return False
    gens = ge.get("generators", [])
    if len(gens) != 1 or not isinstance(gens[0], dict):
        return False
    g = gens[0]
    if g.get("ifs"):
        return False
    lv = g.get("target")
    if not isinstance(lv, str):
        return False
    elt = ge.get("elt", {})
    if not (isinstance(elt, dict) and elt.get("type") == "Call"
            and isinstance(elt.get("func"), str)
            and elt["func"].rsplit(".", 1)[-1] == self_base):
        return False
    eargs = elt.get("args", [])
    if len(eargs) != len(carried) + 1:
        return False
    # leading args = the carried params verbatim (in order); last arg = bound var.
    for a, cname in zip(eargs, carried):
        if not _is_var(a, cname):
            return False
    if not _is_var(eargs[-1], lv):
        return False
    return iter_ok(g.get("iter", {}), lv)


def recognize_type_existence(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the IRScanner `obj: Any` type-existence fold.
    Returns {subject, tag} or None. Never raises."""
    try:
        return _recognize_type_existence(func)
    except Exception:
        return None


def _recognize_type_existence(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if not params:
        return None
    # The Any-tree subject is the LAST param; any LEADING params are "carried"
    # scalars threaded verbatim through the whole fold group (the
    # `is_recursive(name, obj)` shape — `name: str` is compared inside the
    # discriminant and passed unchanged into every self-call). Each carried param
    # MUST be an annotated `str`: the only carried lowering the discriminant +
    # emitter model is the string-key equality `<subj>.get("<k>") == <carried>`.
    subj = params[-1]
    carried = list(params[:-1])
    pa = func.get("param_annotations", {}) or {}
    # genuinely UNTYPED `Any` subject only (an annotated `list`/`set`/record
    # subject is a different recogniser's shape).
    if subj in pa:
        return None
    for c in carried:
        if pa.get(c) != "str":
            return None
    if func.get("return_annotation") != "bool":
        return None
    body = func.get("body", [])
    if len(body) != 3:
        return None
    if_dict, if_list, tail = body
    # tail: `return False`
    if not (isinstance(tail, dict) and tail.get("stmt") == "Return"
            and isinstance(tail.get("value"), dict)
            and tail["value"].get("type") == "Bool"
            and tail["value"].get("value") is False):
        return None
    # self_base = the method's own name, i.e. everything after the `<classlower>__`
    # prefix. Split on the FIRST `__` (the class-method boundary), NOT the last:
    # a lambda-lifted nested `def _check` mangles to `irscanner___check`
    # (`irscanner` + `__` + `_check`), and `rsplit("__",1)` would eat the method's
    # leading underscore -> "check", which no longer equals the genexp self-call's
    # basename "_check" (recognition silently fails). A class-lowered name never
    # contains `__` (CamelCase collapses to an underscore-free run), so `split`
    # is identical to `rsplit` for every single-`__` method name (the 6 already
    # converted) and strictly more correct for a leading-`_` / internal-`__` name.
    self_base = (func.get("name") or "").rsplit(".", 1)[-1].split("__", 1)[-1]
    # if_dict: if isinstance(obj, dict): [ if obj.get("type")=="<TAG>": return True,
    #                                      return any(self(v) for v in obj.values()) ]
    if not (isinstance(if_dict, dict) and if_dict.get("stmt") == "If"
            and not if_dict.get("orelse")
            and _match_isinstance(if_dict.get("test", {}), subj, "dict")):
        return None
    # dict-arm body = N>=1 `if <disc>: return True` tag-guards followed by the
    # `return any(self(v) for v in obj.values())` recursion. The 6+`_check`+
    # `is_recursive` have exactly ONE tag-guard; `uses_array_lit` has TWO (a plain
    # `type=="ArrayLit"` arm and a nested `type=="BinOp" and op=="*" and
    # obj["left"].get("type")=="ArrayLit"` arm) — a DISJUNCTION, ORed in the emitter.
    db = if_dict.get("body", [])
    if len(db) < 2:
        return None
    tag_ifs, dret = db[:-1], db[-1]
    preds: List[Dict[str, Any]] = []
    for tag_if in tag_ifs:
        if not (isinstance(tag_if, dict) and tag_if.get("stmt") == "If"
                and not tag_if.get("orelse")):
            return None
        pr = _match_type_discriminant(tag_if.get("test", {}), subj, carried)
        if pr is None:
            return None
        if not (len(tag_if.get("body", [])) == 1
                and _is_bool_true_return(tag_if["body"][0])):
            return None
        preds.append(pr)
    if not (isinstance(dret, dict) and dret.get("stmt") == "Return"):
        return None

    def _values_iter(it: Any, lv: str) -> bool:
        return (isinstance(it, dict) and it.get("type") == "Call"
                and it.get("func") == f"{subj}.values" and not it.get("args"))

    if not _match_any_selfrecurse_genexp(dret.get("value", {}), subj,
                                         self_base, _values_iter, carried):
        return None
    # if_list: if isinstance(obj, list): return any(self(x) for x in obj)
    if not (isinstance(if_list, dict) and if_list.get("stmt") == "If"
            and not if_list.get("orelse")
            and _match_isinstance(if_list.get("test", {}), subj, "list")):
        return None
    lb = if_list.get("body", [])
    if len(lb) != 1:
        return None
    lret = lb[0]
    if not (isinstance(lret, dict) and lret.get("stmt") == "Return"):
        return None

    def _subj_iter(it: Any, lv: str) -> bool:
        return _is_var(it, subj)

    if not _match_any_selfrecurse_genexp(lret.get("value", {}), subj,
                                         self_base, _subj_iter, carried):
        return None
    return {"subject": subj, "preds": preds, "carried": carried}


def emit_type_existence_group(func: Dict[str, Any], desc: Dict[str, Any],
                              whyml_ident) -> List[str]:
    """Emit the certified scalar-rooted pyval/pydict/list-pyval type-existence
    catamorphism for a recognised IRScanner `uses_<X>(obj)` predicate.

    Structurally identical to `emit_bool_existence_group` (the proven A-bool
    OR-fold over the SAME L1 `pyval` theory) except: (a) rooted at a SCALAR
    `pyval` `obj` instead of a `list pyval` subject, and (b) the discriminant
    reader is keyed on the INTERNED "type" key (`K_type`) rather than the
    computed "stmt" key. The recursion is on DIRECT structural sub-terms (the
    `v` of `DCons`, the `h`/`t` of `Cons`), so each `variant` (`pv_size`/
    `size_dict`/`size_list`) decreases syntactically. The recognised tag drives
    the true-arm (`{n}__type_is obj "<tag>"`) — the mutation-sensitive,
    non-facade signal. `obj` appears in the emitted body (de-vacuified,
    wall-lessons (l))."""
    n = whyml_ident(func["name"])
    preds = desc["preds"]
    # `is_recursive(name, obj)`: leading scalar-`str` params carried verbatim
    # through the whole rec group (declared `(c: string)`, threaded into every
    # self-call). Empty for the plain `uses_<X>(obj)` shape (byte-inert there).
    cids = [whyml_ident(c) for c in desc.get("carried", [])]
    cdecl = "".join(f" ({c}: string)" for c in cids)   # declaration positions
    cargs = "".join(f" {c}" for c in cids)             # call-site threading
    # interned irkey constant per read key (theory `get d K_<key>` / the DCons cell).
    _IRKEY = {"type": "K_type", "left": "K_left", "right": "K_right",
              "op": "K_op", "value": "K_value", "target": "K_target",
              "body": "K_body", "orelse": "K_orelse", "func": "K_func",
              "name": "K_name"}
    out: List[str] = []
    _emitted: set = set()

    def _emit_key_reader(key: str) -> None:
        # interned-named-key reader (option string over the K_<key> cell) +
        # `<key>_is` predicate — the `_emit_stmt_reader` shape, interned variant.
        if key in _emitted:
            return
        _emitted.add(key)
        kc = _IRKEY[key]
        out.append(f"  let rec {n}__get_{key} (d: pydict) : option string")
        out.append("    variant { d }")
        out.append("  = match d with DNil -> None")
        out.append(f"    | DCons {kc} (PStr s) rest -> Some s")
        out.append(f"    | DCons _ _ rest -> {n}__get_{key} rest end")
        out.append(f"  let function {n}__{key}_is (v: pyval) (tag: string) : bool")
        out.append("  = match v with")
        out.append(f"    | PDict d -> (match {n}__get_{key} d with"
                   f" Some t -> pystr_eq t tag | None -> false end)")
        out.append("    | _ -> false end")

    def _emit_childp_reader(nkey: str) -> None:
        # option-pyval projector for the interned K_<nkey> cell — the direct
        # DCons-constructor match (the SAME style as the string `_emit_key_reader`,
        # returning the raw child `v` instead of its PStr). Avoids the theory `get`
        # (its unqualified name mis-resolves in this scope).
        if ("childp", nkey) in _emitted:
            return
        _emitted.add(("childp", nkey))
        kc = _IRKEY[nkey]
        out.append(f"  let rec {n}__getp_{nkey} (d: pydict) : option pyval")
        out.append("    variant { d }")
        out.append("  = match d with DNil -> None")
        out.append(f"    | DCons {kc} v rest -> Some v")
        out.append(f"    | DCons _ _ rest -> {n}__getp_{nkey} rest end")

    def _emit_nested_reader(nkey: str, subkey: str) -> None:
        # `<subj>["<nkey>"].get("<subkey>") == tag` -> read the K_<nkey> child pyval
        # then apply the CHILD's `<subkey>_is`. A non-PDict child makes `<subkey>_is`
        # return false (subsumes the source's `isinstance(obj["<nkey>"], dict)` guard).
        _emit_key_reader(subkey)
        _emit_childp_reader(nkey)
        tag = ("nested", nkey, subkey)
        if tag in _emitted:
            return
        _emitted.add(tag)
        out.append(f"  let function {n}__nested_{nkey}_{subkey}_is"
                   f" (v: pyval) (tag: string) : bool")
        out.append("  = match v with")
        out.append(f"    | PDict d -> (match {n}__getp_{nkey} d with"
                   f" Some c -> {n}__{subkey}_is c tag | None -> false end)")
        out.append("    | _ -> false end")

    def _fact_str(f: Dict[str, Any]) -> str:
        if f["t"] == "keylit":
            _emit_key_reader(f["key"])
            return f'{n}__{f["key"]}_is obj "{f["tag"]}"'
        if f["t"] == "keyin":
            _emit_key_reader(f["key"])
            mem = " || ".join(f'{n}__{f["key"]}_is obj "{t}"' for t in f["tags"])
            return f"({mem})"
        if f["t"] == "keyparam":
            _emit_key_reader(f["key"])
            return f'{n}__{f["key"]}_is obj {whyml_ident(f["param"])}'
        # proj
        _emit_nested_reader(f["key"], f["subkey"])
        return f'{n}__nested_{f["key"]}_{f["subkey"]}_is obj "{f["tag"]}"'

    def _arm_str(pred: Dict[str, Any]) -> str:
        _emit_key_reader("type")
        if pred["kind"] == "simple":
            return f'{n}__type_is obj "{pred["tag"]}"'
        if pred["kind"] == "param":
            # `type=="<T>" and <k2>==<carried param>` — the second reader compares the
            # interned key's PStr value against the runtime carried string (not a
            # literal): `{n}__<k2>_is obj <param>` (`func_is obj name`).
            _emit_key_reader(pred["key2"])
            pval = whyml_ident(pred["param"])
            return (f'{n}__type_is obj "{pred["type_tag"]}"'
                    f' && {n}__{pred["key2"]}_is obj {pval}')
        if pred["kind"] == "nested":
            facts = " && ".join(_fact_str(f) for f in pred["facts"])
            return f'{n}__type_is obj "{pred["type_tag"]}" && {facts}'
        # compound
        _emit_key_reader(pred["key2"])
        mem = " || ".join(f'{n}__{pred["key2"]}_is obj "{t}"' for t in pred["tags"])
        return f'{n}__type_is obj "{pred["type_tag"]}" && ({mem})'

    # DISJUNCTION of all recognised dict tag-arms (`uses_array_lit` has 2; every
    # other predicate exactly 1 — a single arm keeps the emitted string identical
    # to the pre-multi-arm output, so the 8 already-converted stay byte-stable).
    if len(preds) == 1:
        pdict_arm = _arm_str(preds[0])
    else:
        pdict_arm = " || ".join(f"({_arm_str(p)})" for p in preds)
    # scalar-rooted mutual catamorphism into bool (R2d rec-group fold); the
    # carried params are threaded (declared once per member, passed on each call).
    out.append(f"  let rec {n}{cdecl} (obj: pyval) : bool")
    out.append("    requires { true } ensures { true } variant { pv_size obj }")
    out.append("  = match obj with")
    out.append(f"    | PDict d -> {pdict_arm} || {n}__d{cargs} d")
    out.append(f"    | PList xs -> {n}__l{cargs} xs")
    out.append("    | _ -> false end")
    out.append(f"  with {n}__d{cdecl} (d: pydict) : bool")
    out.append("    requires { true } ensures { true } variant { size_dict d }")
    out.append(f"  = match d with DNil -> false"
               f" | DCons _ v rest -> {n}{cargs} v || {n}__d{cargs} rest end")
    out.append(f"  with {n}__l{cdecl} (xs: list pyval) : bool")
    out.append("    requires { true } ensures { true } variant { size_list xs }")
    out.append(f"  = match xs with Nil -> false"
               f" | Cons h t -> {n}{cargs} h || {n}__l{cargs} t end")
    return out


# =========================================================================
# NAMED-FIELD self-recursive existence fold — recognize_named_field_existence.
#
# genexp-erasure-wall / wall-lessons (l),(j),(q): a SINGLE untyped-node
# existence predicate that (a) reads its discriminant into a local via a
# `.get("<KEY>")` on a NON-`type` key, (b) returns True on a literal tag, and
# (c) recurses over a NAMED LIST FIELD via `any(self(a) for a in
# obj.get("<FIELD>", []))` — the `_pattern_has_constructor` shape:
#
#     def _pattern_has_constructor(pat):
#         p = pat.get("pattern")
#         if p == "Constructor":
#             return True
#         if p == "Or":
#             return any(self._pattern_has_constructor(a)
#                        for a in pat.get("alternatives", []))
#         return False
#
# Before this, the `any(genexp)` collapsed to `any_1 (Array.make 1 0)` (an
# UNCONSTRAINED oracle over a fabricated argument) — a fully vacuous facade the
# mutation test cannot see (wall-lessons (l), bin/check-emitted-vacuity.py).
# This emits the SAME certified scalar-rooted pyval/pydict/list-pyval
# catamorphism as `emit_type_existence_group` (no new ADT, no new certificate,
# ledger 3), differing only in (i) the discriminant key is read via the
# `K_dyn "<key>"` computed-key cell (the theory's built-in dynamic-key
# fallback — no new interned constant) rather than `K_type`, and (ii) the shape
# is `[assign, if-tag, if-recurse, return-False]` rather than the isinstance
# dict/list arms. The named-field recursion is subsumed by the universal
# structural descend (insight-C over-approximation — the SAME doctrine the 8
# IRScanner predicates use to drop `.values()`/membership conjuncts): the fold
# OR-descends every sub-term, so the `alternatives` list (one child cell) is
# covered, and the emitted body matches on the real subject param + drives the
# true-arm off the literal tag (the mutation-sensitive, non-facade signal;
# `<subj>` appears in the body, de-vacuified). Fail-closed; a body-fidelity bug
# yields a loud unprovable instance, never a false proof.
# =========================================================================


def recognize_named_field_existence(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the single-node named-field self-recursive
    existence fold (`_pattern_has_constructor` shape). Returns
    {subject, key, tags} or None. Never raises."""
    try:
        return _recognize_named_field_existence(func)
    except Exception:
        return None


def _recognize_named_field_existence(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    subj = params[0]
    pa = func.get("param_annotations", {}) or {}
    # genuinely UNTYPED `Any` subject only (an annotated subject is a
    # different recogniser's shape — the pyval carrier is for untyped nodes).
    if subj in pa:
        return None
    if func.get("return_annotation") != "bool":
        return None
    body = func.get("body", [])
    if len(body) != 4:
        return None
    assign, if_a, if_b, tail = body
    # tail: `return False`
    if not (isinstance(tail, dict) and tail.get("stmt") == "Return"
            and isinstance(tail.get("value"), dict)
            and tail["value"].get("type") == "Bool"
            and tail["value"].get("value") is False):
        return None
    # assign: `p = <subj>.get("<KEY>")` — the discriminant read into a local.
    if not (isinstance(assign, dict) and assign.get("stmt") == "Assign"):
        return None
    dispatch_var = assign.get("target")
    if not isinstance(dispatch_var, str):
        return None
    key = _match_get_call(assign.get("value", {}), subj)
    if key is None:
        return None
    # if_a: `if p == "<TAG>": return True` (the decisive-tag arm).
    if not (isinstance(if_a, dict) and if_a.get("stmt") == "If"
            and not if_a.get("orelse")):
        return None
    tags_a = _match_stype_tag_or_tags(if_a.get("test", {}), dispatch_var)
    if not tags_a:
        return None
    if not (len(if_a.get("body", [])) == 1
            and _is_bool_true_return(if_a["body"][0])):
        return None
    # if_b: `if p == "<TAG2>": return any(self(a) for a in <subj>.get("<F>", []))`
    if not (isinstance(if_b, dict) and if_b.get("stmt") == "If"
            and not if_b.get("orelse")):
        return None
    if not _match_stype_tag_or_tags(if_b.get("test", {}), dispatch_var):
        return None
    bb = if_b.get("body", [])
    if len(bb) != 1:
        return None
    bret = bb[0]
    if not (isinstance(bret, dict) and bret.get("stmt") == "Return"):
        return None
    self_base = (func.get("name") or "").rsplit(".", 1)[-1].split("__", 1)[-1]

    def _field_iter(it: Any, lv: str) -> bool:
        # the recursion iterable is a named-field read `<subj>.get("<F>", [])`
        # (any literal field; the descend subsumes it — insight-C).
        return _match_get_call(it, subj) is not None

    if not _match_any_selfrecurse_genexp(bret.get("value", {}), subj,
                                         self_base, _field_iter):
        return None
    return {"subject": subj, "key": key, "tags": list(tags_a)}


def emit_named_field_existence_group(func: Dict[str, Any], desc: Dict[str, Any],
                                     whyml_ident) -> List[str]:
    """Emit the certified scalar-rooted pyval/pydict/list-pyval existence
    catamorphism for a recognised named-field self-recursive predicate
    (`_pattern_has_constructor`). Structurally identical to
    `emit_type_existence_group` (the proven L1 `pyval` OR-fold) except the
    discriminant is keyed on the `K_dyn "<key>"` dynamic-key cell (the
    theory's computed-key fallback — no new interned constant, no theory
    change) instead of the interned `K_type`. The recognised tag drives the
    true-arm (`{n}__key_is <subj> "<tag>"`) — the mutation-sensitive,
    non-facade signal. `<subj>` appears in the emitted body (de-vacuified,
    wall-lessons (l)); recursion terminates on the structural `pv_size`
    measure (certified variant, NO `any_1`/int-hash)."""
    n = whyml_ident(func["name"])
    subj_id = whyml_ident(desc["subject"])
    key = desc["key"]
    tags = desc["tags"]
    _IRKEY = {"type": "K_type", "left": "K_left", "right": "K_right",
              "op": "K_op", "value": "K_value", "target": "K_target",
              "body": "K_body", "orelse": "K_orelse", "func": "K_func",
              "name": "K_name"}
    out: List[str] = []
    # interned-or-dynamic key reader (option string over the matched cell).
    out.append(f"  let rec {n}__get (d: pydict) : option string")
    out.append("    variant { d }")
    out.append("  = match d with DNil -> None")
    if key in _IRKEY:
        out.append(f"    | DCons {_IRKEY[key]} (PStr s) rest -> Some s")
    else:
        out.append(f"    | DCons (K_dyn ks) (PStr s) rest ->"
                   f' if pystr_eq ks "{key}" then Some s else {n}__get rest')
    out.append(f"    | DCons _ _ rest -> {n}__get rest end")
    out.append(f"  let function {n}__key_is (v: pyval) (tag: string) : bool")
    out.append("  = match v with")
    out.append(f"    | PDict d -> (match {n}__get d with"
               f" Some t -> pystr_eq t tag | None -> false end)")
    out.append("    | _ -> false end")
    # DISJUNCTION of the decisive-tag arm(s) (a single tag for the
    # `_pattern_has_constructor` shape; the `in (...)` form yields several).
    tag_disj = " || ".join(f'{n}__key_is {subj_id} "{t}"' for t in tags)
    # scalar-rooted mutual catamorphism into bool (the R2d rec-group fold —
    # the fold co-lives with the recursive predicate so the self-recursion
    # binds and terminates on the structural pyval measure).
    out.append(f"  let rec {n} ({subj_id}: pyval) : bool")
    out.append("    requires { true } ensures { true }"
               f" variant {{ pv_size {subj_id} }}")
    out.append(f"  = match {subj_id} with")
    out.append(f"    | PDict d -> {tag_disj} || {n}__d d")
    out.append(f"    | PList xs -> {n}__l xs")
    out.append("    | _ -> false end")
    out.append(f"  with {n}__d (d: pydict) : bool")
    out.append("    requires { true } ensures { true } variant { size_dict d }")
    out.append(f"  = match d with DNil -> false"
               f" | DCons _ v rest -> {n} v || {n}__d rest end")
    out.append(f"  with {n}__l (xs: list pyval) : bool")
    out.append("    requires { true } ensures { true } variant { size_list xs }")
    out.append(f"  = match xs with Nil -> false"
               f" | Cons h t -> {n} h || {n}__l t end")
    return out


# ============================================================================
# pyval-walker-impl.md (driver-backlog item 3) — the GENERAL value-returning
# pyval string walker. Unlike the bool-existence family (return bool) this is a
# string-RETURNING catamorphism over a heterogeneous nested-tuple/list param
# (the sertop s-expression / `from_sexp` shape): `isinstance(t, tuple)` guards,
# POSITIONAL index `t[i]`, string-literal tag dispatch `t[0] == "..."`, `len(t)`
# length guards, a `for x in t` fold with EARLY string-return, all lowered onto
# the certified `pyval` ADT (PStr=atom, PList=tuple) via three small TOTAL
# projectors (pv_nth/pv_len/atom_of, emitted inline, NO axiom — the pyval
# `pv_size` cert already covers measure/termination; ledger stays 3).
#
# This is a STRUCTURAL translator, not a shape matcher: it recursively lowers an
# arbitrary composition of the supported fragment (below), so the emitted `.mlw`
# is a faithful function of the body — the mutation test (change a literal / an
# index / a guard → the emitted body changes) passes by construction. Any node
# outside the fragment raises `_PVWBail` and the recognizer returns None
# (precision-over-recall, fail-closed: a miss keeps the stub `\trusted`, never a
# false fire). The templater is NOT in the TCB — a bug yields an unprovable
# instance (the whole-file re-proof is loud), never a false proof.
#
# Supported fragment (single `Any` param `p`, `-> Optional[str]` union return):
#   test  ::= not test | test and test | test or test
#           | isinstance(vref, tuple|list|dict|str)
#           | len(vref) (>=|>|<=|<|==) <int>
#           | vref == "<lit>" | "<lit>" == vref          (atom/tag compare)
#   vref  ::= <var> | vref[<int>]                        (a pyval-typed term)
#   stmt  ::= return None | return <strexpr>
#           | <var> = vref
#           | if test: stmts [else: stmts]
#           | for <var> in vref: stmts                   (fold w/ early return)
#   strexpr ::= "<lit>" | vref                           (vref -> atom_of)

class _PVWBail(Exception):
    """Raised on any node outside the supported fragment (fail-closed)."""


def _pvw_mv(name: str) -> str:
    """Mangle a source variable name to a keyword-safe WhyML identifier
    (`val` is a WhyML keyword; a uniform `v_` prefix dodges every clash)."""
    return "v_" + name


def _pvw_strlit(s: str) -> str:
    """A WhyML string literal, fail-closed on quote/backslash (no escaping)."""
    if '"' in s or "\\" in s:
        raise _PVWBail()
    return '"' + s + '"'


def _pvw_valref(node: Any, ctx: Dict[str, Any]) -> str:
    """Translate a Var / positional-Subscript into a pyval-typed WhyML term."""
    if _is_var(node):
        nm = node.get("name")
        if nm not in ctx["scope"]:
            raise _PVWBail()
        return _pvw_mv(nm)
    if isinstance(node, dict) and node.get("type") == "Subscript":
        base = _pvw_valref(node.get("value"), ctx)
        idx = node.get("index")
        if not (isinstance(idx, dict) and idx.get("type") == "Number"):
            raise _PVWBail()
        i = idx.get("value")
        if not isinstance(i, int) or i < 0:
            raise _PVWBail()
        return f'({ctx["p"]}pnth {base} {i})'
    raise _PVWBail()


def _pvw_strexpr(node: Any, ctx: Dict[str, Any]) -> str:
    """Translate an expression used in a STRING context (return / tag compare):
    a literal stays a literal; a pyval vref is coerced by `atom_of`."""
    s = _is_string(node)
    if s is not None:
        return _pvw_strlit(s)
    return f'({ctx["p"]}atom {_pvw_valref(node, ctx)})'


def _pvw_isinstance(node: Any, ctx: Dict[str, Any]) -> str:
    if node.get("func") != "isinstance":
        raise _PVWBail()
    args = node.get("args", [])
    if len(args) != 2 or not _is_var(args[1]):
        raise _PVWBail()
    base = _pvw_valref(args[0], ctx)
    cls = args[1].get("name")
    if cls in ("tuple", "list"):
        return f"(is_plist {base})"
    if cls == "dict":
        return f"(is_pdict {base})"
    if cls == "str":
        return f"(is_pstr {base})"
    raise _PVWBail()


def _pvw_lencmp(left: Any, op: str, right: Any, ctx: Dict[str, Any]) -> str:
    if not (isinstance(left, dict) and left.get("type") == "Call"
            and left.get("func") == "len" and len(left.get("args", [])) == 1):
        raise _PVWBail()
    if not (isinstance(right, dict) and right.get("type") == "Number"
            and isinstance(right.get("value"), int)):
        raise _PVWBail()
    base = _pvw_valref(left["args"][0], ctx)
    return f'({ctx["p"]}plen {base} {op} {right["value"]})'


def _pvw_eq(left: Any, right: Any, ctx: Dict[str, Any]) -> str:
    ls, rs = _is_string(left), _is_string(right)
    if rs is not None and ls is None:
        return f"(pystr_eq {_pvw_strexpr(left, ctx)} {_pvw_strlit(rs)})"
    if ls is not None and rs is None:
        return f"(pystr_eq {_pvw_strexpr(right, ctx)} {_pvw_strlit(ls)})"
    raise _PVWBail()


def _pvw_test(node: Any, ctx: Dict[str, Any]) -> str:
    if not isinstance(node, dict):
        raise _PVWBail()
    t = node.get("type")
    if t == "UnaryOp" and node.get("op") == "not":
        return f"(not {_pvw_test(node.get('expr'), ctx)})"
    if t == "BinOp":
        op = node.get("op")
        if op in ("and", "or"):
            l = _pvw_test(node.get("left"), ctx)
            r = _pvw_test(node.get("right"), ctx)
            return f"({l} {'&&' if op == 'and' else '||'} {r})"
        if op == "==":
            return _pvw_eq(node.get("left"), node.get("right"), ctx)
        if op in (">=", ">", "<=", "<"):
            return _pvw_lencmp(node.get("left"), op, node.get("right"), ctx)
        raise _PVWBail()
    if t == "Call":
        return _pvw_isinstance(node, ctx)
    raise _PVWBail()


def _pvw_return(value: Any, ctx: Dict[str, Any]) -> str:
    if isinstance(value, dict) and value.get("type") == "None":
        return ctx["none_ctor"]
    return f"({ctx['some_ctor']} {_pvw_strexpr(value, ctx)})"


def _pvw_stmts(stmts: Any, cont: str, ctx: Dict[str, Any]) -> str:
    """Translate a statement list into a WhyML expression of the union return
    type; `cont` is the fall-through value when the list is exhausted."""
    if not isinstance(stmts, list):
        raise _PVWBail()
    if not stmts:
        return cont
    s0, rest = stmts[0], stmts[1:]
    if not isinstance(s0, dict):
        raise _PVWBail()
    kind = s0.get("stmt")
    if kind == "Return":
        return _pvw_return(s0.get("value"), ctx)          # terminal
    if kind == "Assign":
        tgt = s0.get("target")
        if not isinstance(tgt, str):
            raise _PVWBail()
        rhs = _pvw_valref(s0.get("value"), ctx)           # RHS is a pyval term
        newctx = dict(ctx); newctx["scope"] = ctx["scope"] | {tgt}
        return f"(let {_pvw_mv(tgt)} = {rhs} in {_pvw_stmts(rest, cont, newctx)})"
    if kind == "If":
        contrest = _pvw_stmts(rest, cont, ctx)
        test = _pvw_test(s0.get("test"), ctx)
        thenb = _pvw_stmts(s0.get("body", []), contrest, ctx)
        elseb = _pvw_stmts(s0.get("orelse") or [], contrest, ctx)
        return f"(if {test} then {thenb} else {elseb})"
    if kind == "For":
        tgt = s0.get("target")
        if not isinstance(tgt, str):
            raise _PVWBail()
        itref = _pvw_valref(s0.get("iter"), ctx)
        k = ctx["counter"][0]; ctx["counter"][0] += 1
        loop = f"{ctx['n']}__loop{k}"
        rv = f"{loop}_rest"
        aftercont = _pvw_stmts(rest, cont, ctx)           # Nil case
        newctx = dict(ctx); newctx["scope"] = ctx["scope"] | {tgt}
        lbody = _pvw_stmts(s0.get("body", []), f"({loop} {rv})", newctx)
        return (f"(let rec {loop} (l: list pyval) : {ctx['ret']}\n"
                f"     variant {{ l }}\n"
                f"   = match l with Nil -> {aftercont}\n"
                f"     | Cons {_pvw_mv(tgt)} {rv} -> {lbody} end\n"
                f"   in {loop} (match {itref} with PList xs -> xs | _ -> Nil end))")
    raise _PVWBail()


def _pvw_body_reads(stmts: Any) -> bool:
    """True iff the body contains a positional Subscript or a For over the param
    (a genuine pyval read) — the non-vacuity floor (wall-lessons (l))."""
    def walk(node: Any) -> bool:
        if isinstance(node, dict):
            if node.get("type") == "Subscript" or node.get("stmt") == "For":
                return True
            return any(walk(v) for v in node.values())
        if isinstance(node, list):
            return any(walk(x) for x in node)
        return False
    return walk(stmts)


def recognize_pyval_string_walker(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the general value-returning pyval string walker.
    Returns {param} or None. Never raises."""
    try:
        return _recognize_pyval_string_walker(func)
    except Exception:
        return None


def _recognize_pyval_string_walker(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    p = params[0]
    if func.get("param_annotations", {}).get(p) not in (None, "Any"):
        return None
    ret = func.get("return_annotation")
    if not (isinstance(ret, str) and ret.startswith("_union_")):
        return None
    body = func.get("body", [])
    if not _pvw_body_reads(body):
        return None
    # Dry-run structural translation (placeholder ctors). Any unsupported node
    # raises _PVWBail -> recognizer returns None. This IS the fail-closed gate.
    ctx = {"n": "f", "p": "f__", "scope": {p}, "ret": ret,
           "some_ctor": "S", "none_ctor": "N", "counter": [0]}
    _pvw_stmts(body, "N", ctx)
    return {"param": p}


def emit_pyval_string_walker_group(func: Dict[str, Any], desc: Dict[str, Any],
                                   whyml_ident) -> List[str]:
    """Emit the general value-returning pyval string walker: three inline TOTAL
    projectors (pv_nth/pv_len/atom_of over the certified pyval ADT, axiom-free,
    structurally terminating) + the structurally-translated body as a function
    returning the synthesized Optional[str] union. `desc` carries the resolved
    union: {param, ret_whyml, some_ctor, none_ctor} (filled at the dispatch site
    from `self._variant_types`)."""
    n = whyml_ident(func["name"])
    P = f"{n}__"
    param = desc["param"]
    ctx = {"n": n, "p": P, "scope": {param}, "ret": desc["ret_whyml"],
           "some_ctor": desc["some_ctor"], "none_ctor": desc["none_ctor"],
           "counter": [0]}
    body = _pvw_stmts(func.get("body", []), desc["none_ctor"], ctx)
    out: List[str] = []
    # ---- inline TOTAL projectors (no axiom; pv_size cert covers the measure) --
    out.append(f"  let rec function {P}nthl (l: list pyval) (i: int) : pyval")
    out.append("    variant { l }")
    out.append(f"  = match l with Nil -> PNone"
               f" | Cons h t -> if i <= 0 then h else {P}nthl t (i - 1) end")
    out.append(f"  let function {P}pnth (v: pyval) (i: int) : pyval")
    out.append(f"  = match v with PList xs -> {P}nthl xs i | _ -> PNone end")
    out.append(f"  let rec function {P}lenl (l: list pyval) : int")
    out.append("    ensures { result >= 0 } variant { l }")
    out.append(f"  = match l with Nil -> 0 | Cons _ t -> 1 + {P}lenl t end")
    out.append(f"  let function {P}plen (v: pyval) : int")
    out.append(f"  = match v with PList xs -> {P}lenl xs | _ -> 0 end")
    out.append(f"  let function {P}atom (v: pyval) : string")
    out.append('  = match v with PStr s -> s | _ -> "" end')
    # ---- the walker ----------------------------------------------------------
    out.append(f"  let {n} ({_pvw_mv(param)}: pyval) : {desc['ret_whyml']}")
    out.append("    requires { true } ensures { true }")
    out.append(f"  = {body}")
    return out


# ============================================================================
# pyval-walker-impl.md C1 (driver-backlog item 3, sexp-carrier residual C1) —
# the LIST-accumulator counterpart of the value-returning pyval string walker.
# Where the string walker RETURNS an `Optional[str]` (single string), this walker
# RETURNS a `List[str]` (`list string`) BUILT by a `.append`/`.extend`/`reversed`
# accumulator over the certified pyval spine (the `from_sexp` `_walk_modpath`/
# `_walk_kername`/`_find_kername_components`/`_full_const_path` shape). It is a
# STRUCTURAL, CPS/state-passing translator (not a shape matcher): each statement
# threads the current `list string` value of every in-scope accumulator, so the
# emitted `.mlw` is a faithful function of the body (mutation test passes by
# construction). Any node outside the fragment raises `_PVWBail` → recognizer
# returns None (precision-over-recall, fail-closed). The templater is NOT in the
# TCB — a bug yields an unprovable instance (the whole-file re-proof is loud),
# never a false proof.
#
# Termination for a TREE self-recursion (`_walk_modpath(mp[1])`) is discharged by
# an axiom-free, per-function `let rec lemma {n}__size_nthl` (in-range element
# size <= list size; the recursion IS the induction, proved by Alt-Ergo — NO new
# axiom, ledger stays 3). The list ops (`app`/`rev`) are inline TOTAL `let rec
# function`s (NO preamble `use list.Append/Reverse` → zero corpus byte-diff).
#
# Supported fragment (single `Any` param `p`, `-> List[str]` (`ret == "list"`)):
#   stmt ::= <acc> = []                         (new list accumulator)
#          | <var> = vref                       (pyval read-binding)
#          | <acc>.append(<strexpr>)
#          | <acc>.extend(<listexpr>)
#          | if <test>: stmts [else: stmts]
#          | for <var> in vref: stmts           (single-accumulator fold)
#          | return <acc> | return []
#   listexpr ::= <acc> | reversed(<acc>) | <selfname>(vref)   (self-recursion)
#   test extends the string-walker fragment with a bare `vref` (tuple truthiness
#        -> `plen vref > 0`).

def _pvl_copy(state: Dict[str, Any]) -> Dict[str, Any]:
    return {"acc": dict(state["acc"]), "scope": set(state["scope"])}


def _pvl_freshacc(ctx: Dict[str, Any], name: str) -> str:
    k = ctx["counter"][0]
    ctx["counter"][0] += 1
    return f"v_{name}_{k}"


def _pvl_test(node: Any, ctx: Dict[str, Any]) -> str:
    """String-walker test fragment + bare-`vref` tuple truthiness."""
    if _is_var(node):
        nm = node.get("name")
        if nm not in ctx["scope"]:
            raise _PVWBail()
        return f'({ctx["p"]}plen {_pvw_mv(nm)} > 0)'
    if not isinstance(node, dict):
        raise _PVWBail()
    t = node.get("type")
    if t == "UnaryOp" and node.get("op") == "not":
        return f"(not {_pvl_test(node.get('expr'), ctx)})"
    if t == "BinOp":
        op = node.get("op")
        if op in ("and", "or"):
            l = _pvl_test(node.get("left"), ctx)
            r = _pvl_test(node.get("right"), ctx)
            return f"({l} {'&&' if op == 'and' else '||'} {r})"
        if op == "==":
            return _pvw_eq(node.get("left"), node.get("right"), ctx)
        if op in (">=", ">", "<=", "<"):
            return _pvw_lencmp(node.get("left"), op, node.get("right"), ctx)
        raise _PVWBail()
    if t == "Call":
        return _pvw_isinstance(node, ctx)
    raise _PVWBail()


def _pvl_listexpr(node: Any, state: Dict[str, Any], ctx: Dict[str, Any]) -> str:
    """A `list string`-typed term: an accumulator, `reversed(acc)`, or a
    self-recursive call `<selfname>(vref)`."""
    if _is_var(node):
        nm = node.get("name")
        if nm in state["acc"]:
            return state["acc"][nm]
        raise _PVWBail()
    if isinstance(node, dict) and node.get("type") == "Call":
        f = node.get("func")
        args = node.get("args", [])
        if f == "reversed" and len(args) == 1:
            return f"({ctx['p']}rev {_pvl_listexpr(args[0], state, ctx)})"
        if f == ctx["selfname"] and len(args) == 1:
            return f"({ctx['n']} {_pvw_valref(args[0], ctx)})"
        raise _PVWBail()
    raise _PVWBail()


def _pvl_modified_accs(body: Any, accs: set) -> set:
    """Accumulators (`.append`/`.extend` targets) mutated anywhere in `body`."""
    mods: set = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("stmt") == "Expr":
                call = node.get("value")
                if isinstance(call, dict) and call.get("type") == "Call":
                    f = call.get("func", "")
                    for suf in (".append", ".extend"):
                        if f.endswith(suf) and f[:-len(suf)] in accs:
                            mods.add(f[:-len(suf)])
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)
    walk(body)
    return mods


def _pvl_has_selfcall(body: Any, selfname: str) -> bool:
    def walk(node: Any) -> bool:
        if isinstance(node, dict):
            if (node.get("type") == "Call" and node.get("func") == selfname):
                return True
            return any(walk(v) for v in node.values())
        if isinstance(node, list):
            return any(walk(x) for x in node)
        return False
    return walk(body)


def _pvl_for(s0: Any, kont, ctx: Dict[str, Any], state: Dict[str, Any]) -> str:
    tgt = s0.get("target")
    if not isinstance(tgt, str):
        raise _PVWBail()
    ctx["scope"] = state["scope"]
    itref = _pvw_valref(s0.get("iter"), ctx)
    body = s0.get("body", [])
    mods = _pvl_modified_accs(body, set(state["acc"].keys()))
    if len(mods) != 1:                       # single-accumulator fold only
        raise _PVWBail()
    acc = next(iter(mods))
    k = ctx["counter"][0]; ctx["counter"][0] += 1
    loop = f"{ctx['n']}__lloop{k}"
    pacc = f"{loop}_acc"
    rv = f"{loop}_rest"
    lstate = _pvl_copy(state)
    lstate["acc"][acc] = pacc
    lstate["scope"].add(tgt)

    def loopkont(st: Dict[str, Any]) -> str:
        return f"({loop} {rv} {st['acc'][acc]})"

    lbody = _pvl_stmts(body, lstate, loopkont, ctx)
    mv = _pvl_freshacc(ctx, acc)
    st2 = _pvl_copy(state)
    st2["acc"][acc] = mv
    spine = f"(match {itref} with PList xs -> xs | _ -> Nil end)"
    return (f"(let rec {loop} (l: list pyval) ({pacc}: list string) : list string\n"
            f"     variant {{ l }}\n"
            f"   = match l with Nil -> {pacc}\n"
            f"     | Cons {_pvw_mv(tgt)} {rv} -> {lbody} end\n"
            f"   in let {mv} = {loop} {spine} {state['acc'][acc]} in {kont(st2)})")


def _pvl_stmts(stmts: Any, state: Dict[str, Any], k, ctx: Dict[str, Any]) -> str:
    """CPS translate a statement list into a `list string` expression; `k` is the
    fall-through continuation (a Python callable state->str). Every path must end
    in an explicit `return` (else the top-level `k` raises _PVWBail)."""
    if not isinstance(stmts, list):
        raise _PVWBail()
    ctx["scope"] = state["scope"]
    if not stmts:
        return k(state)
    s0, rest = stmts[0], stmts[1:]
    if not isinstance(s0, dict):
        raise _PVWBail()

    def kont(st: Dict[str, Any]) -> str:
        return _pvl_stmts(rest, st, k, ctx)

    kind = s0.get("stmt")
    if kind == "Assign":
        tgt = s0.get("target")
        if not isinstance(tgt, str):
            raise _PVWBail()
        val = s0.get("value")
        if (isinstance(val, dict) and val.get("type") == "ArrayLit"
                and not val.get("elts")):
            mv = _pvl_freshacc(ctx, tgt)
            st2 = _pvl_copy(state)
            st2["acc"][tgt] = mv
            return f"(let {mv} = (Nil: list string) in {kont(st2)})"
        rhs = _pvw_valref(val, ctx)          # pyval read-binding
        st2 = _pvl_copy(state)
        st2["scope"].add(tgt)
        return f"(let {_pvw_mv(tgt)} = {rhs} in {kont(st2)})"
    if kind == "Expr":
        call = s0.get("value")
        if not (isinstance(call, dict) and call.get("type") == "Call"):
            raise _PVWBail()
        f = call.get("func", "")
        args = call.get("args", [])
        if f.endswith(".append") and len(args) == 1:
            acc = f[:-len(".append")]
            if acc not in state["acc"]:
                raise _PVWBail()
            se = _pvw_strexpr(args[0], ctx)
            cur = state["acc"][acc]
            mv = _pvl_freshacc(ctx, acc)
            st2 = _pvl_copy(state)
            st2["acc"][acc] = mv
            return (f"(let {mv} = {ctx['p']}app {cur} "
                    f"(Cons {se} (Nil: list string)) in {kont(st2)})")
        if f.endswith(".extend") and len(args) == 1:
            acc = f[:-len(".extend")]
            if acc not in state["acc"]:
                raise _PVWBail()
            le = _pvl_listexpr(args[0], state, ctx)
            cur = state["acc"][acc]
            mv = _pvl_freshacc(ctx, acc)
            st2 = _pvl_copy(state)
            st2["acc"][acc] = mv
            return f"(let {mv} = {ctx['p']}app {cur} {le} in {kont(st2)})"
        raise _PVWBail()
    if kind == "Return":
        v = s0.get("value")
        if (isinstance(v, dict) and v.get("type") == "ArrayLit"
                and not v.get("elts")):
            return "(Nil: list string)"
        if _is_var(v) and v.get("name") in state["acc"]:
            return state["acc"][v.get("name")]
        raise _PVWBail()
    if kind == "If":
        test = _pvl_test(s0.get("test"), ctx)
        thenb = _pvl_stmts(s0.get("body", []), _pvl_copy(state), kont, ctx)
        elseb = _pvl_stmts(s0.get("orelse") or [], _pvl_copy(state), kont, ctx)
        return f"(if {test} then {thenb} else {elseb})"
    if kind == "For":
        return _pvl_for(s0, kont, ctx, state)
    raise _PVWBail()


def recognize_pyval_list_walker(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Fail-closed match of the pyval List[str]-accumulator walker.
    Returns {param} or None. Never raises."""
    try:
        return _recognize_pyval_list_walker(func)
    except Exception:
        return None


def _recognize_pyval_list_walker(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    p = params[0]
    if func.get("param_annotations", {}).get(p) not in (None, "Any"):
        return None
    ret = func.get("return_annotation")
    if ret not in ("list", "List"):
        return None
    body = func.get("body", [])
    if not _pvw_body_reads(body):
        return None
    # Dry-run structural translation (placeholder names). Any unsupported node
    # raises _PVWBail -> recognizer returns None. This IS the fail-closed gate.
    ctx = {"n": "f", "p": "f__", "scope": {p}, "counter": [0],
           "selfname": func.get("name")}
    state0 = {"acc": {}, "scope": {p}}

    def k0(_st):
        raise _PVWBail()
    _pvl_stmts(body, state0, k0, ctx)
    return {"param": p}


def emit_pyval_list_walker_group(func: Dict[str, Any], desc: Dict[str, Any],
                                 whyml_ident) -> List[str]:
    """Emit the pyval List[str] walker: inline TOTAL projectors (pv_nth/pv_len/
    atom_of) + inline TOTAL list ops (app/rev) + (when tree self-recursive) an
    axiom-free size lemma, then the CPS-translated body returning `list string`.
    All defined, not axiomatized; ledger stays 3."""
    n = whyml_ident(func["name"])
    P = f"{n}__"
    param = desc["param"]
    ctx = {"n": n, "p": P, "scope": set(), "counter": [0],
           "selfname": func["name"]}
    state0 = {"acc": {}, "scope": {param}}

    def k0(_st):
        raise _PVWBail()
    body = _pvl_stmts(func.get("body", []), state0, k0, ctx)
    self_rec = _pvl_has_selfcall(func.get("body", []), func["name"])
    out: List[str] = []
    # ---- inline TOTAL pyval projectors (axiom-free; pv_size cert = measure) ---
    out.append(f"  let rec function {P}nthl (l: list pyval) (i: int) : pyval")
    out.append("    variant { l }")
    out.append(f"  = match l with Nil -> PNone"
               f" | Cons h t -> if i <= 0 then h else {P}nthl t (i - 1) end")
    out.append(f"  let function {P}pnth (v: pyval) (i: int) : pyval")
    out.append(f"  = match v with PList xs -> {P}nthl xs i | _ -> PNone end")
    out.append(f"  let rec function {P}lenl (l: list pyval) : int")
    out.append("    ensures { result >= 0 } variant { l }")
    out.append(f"  = match l with Nil -> 0 | Cons _ t -> 1 + {P}lenl t end")
    out.append(f"  let function {P}plen (v: pyval) : int")
    out.append(f"  = match v with PList xs -> {P}lenl xs | _ -> 0 end")
    out.append(f"  let function {P}atom (v: pyval) : string")
    out.append('  = match v with PStr s -> s | _ -> "" end')
    # ---- inline TOTAL list ops (self-contained: no preamble use → byte-inert) -
    out.append(f"  let rec function {P}app (a b: list string) : list string")
    out.append("    variant { a }")
    out.append(f"  = match a with Nil -> b | Cons h t -> Cons h ({P}app t b) end")
    out.append(f"  let rec function {P}revacc (a acc: list string) : list string")
    out.append("    variant { a }")
    out.append(f"  = match a with Nil -> acc | Cons h t -> {P}revacc t (Cons h acc) end")
    out.append(f"  let function {P}rev (a: list string) : list string = {P}revacc a Nil")
    if self_rec:
        # axiom-free size lemma (ledger 3): in-range element size <= list size.
        # The recursion IS the induction; Alt-Ergo discharges the postcondition
        # (calling the certified size_pos / size_list_nonneg cert lemmas).
        out.append(f"  let rec lemma {P}size_nthl (l: list pyval) (i: int) : unit")
        out.append(f"    ensures {{ 0 <= i < {P}lenl l ->"
                   f" pv_size ({P}nthl l i) <= size_list l }}")
        out.append("    variant { l }")
        out.append(f"  = match l with Nil -> () | Cons h t ->"
                   f" size_pos h; size_list_nonneg t; {P}size_nthl t (i - 1) end")
    # ---- the walker ----------------------------------------------------------
    mvp = _pvw_mv(param)
    if self_rec:
        out.append(f"  let rec {n} ({mvp}: pyval) : list string")
        out.append(f"    requires {{ true }} ensures {{ true }}"
                   f" variant {{ pv_size {mvp} }}")
    else:
        out.append(f"  let {n} ({mvp}: pyval) : list string")
        out.append("    requires { true } ensures { true }")
    out.append(f"  = {body}")
    return out
