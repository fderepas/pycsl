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
    out.append(f"    writes {{ {acc} }} variant {{ size {subj} }}")
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


def emit_setfold_group(func: Dict[str, Any], sf: Dict[str, Any],
                       whyml_ident) -> List[str]:
    """Emit the returned-set catamorphism group for a recognized A-set fold.

    Functional (`assigns \\nothing`; no `writes` frame): every function returns
    `map string bool`, combined by the preamble's purely-defined `set_union`.
    Threaded read-only `set` parameters are typed `map string bool` and passed
    through. Congruent (modulo names) to the proven `v2_setfold_spike.mlw`."""
    n = whyml_ident(func["name"])
    subj = sf["subject"]
    extra = sf["extra_params"]
    pre = sf["pre_action"]
    skip = sf["skip_key"]

    extra_sig = "".join(f" ({whyml_ident(e)}: map string bool)" for e in extra)
    extra_args = "".join(f" {whyml_ident(e)}" for e in extra)
    out: List[str] = []

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
    out.append(f"  let rec {n} ({subj}: pyval){extra_sig} : map string bool")
    out.append("    requires { true } ensures { true }")
    out.append(f"    variant {{ size {subj} }}")
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
