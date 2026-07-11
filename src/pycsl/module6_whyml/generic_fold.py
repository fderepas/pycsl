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


def _is_selfcall_1(node: Any, name_box: List[str]) -> bool:
    """A 1-arg Call whose func is a bare name; records the callee in name_box
    (all existence-fold self-calls must share one callee name)."""
    if not (isinstance(node, dict) and node.get("type") == "Call"):
        return False
    f = node.get("func")
    if not isinstance(f, str) or len(node.get("args", [])) != 1:
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

    Returns {subject, self_name, with_value, tag} or None. Never raises."""
    try:
        return _recognize_bool_existence(func)
    except Exception:
        return None


def _recognize_bool_existence(func: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    params = func.get("formal_params", [])
    if len(params) != 1:
        return None
    subj = params[0]
    if func.get("param_annotations", {}).get(subj) != "list":
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
    if tag0 is None:
        # with-value twin: `<stmt>["stmt"]=="Return" and <stmt>.get("value")`
        # — inherently Return-specific (the `.get("value")` guard only makes
        # sense for the Return tag), so this alternate arm-0 shape stays
        # hardcoded to "Return" (it is a DIFFERENT AST shape, not a tag choice).
        if not (isinstance(t0, dict) and t0.get("type") == "BinOp"
                and t0.get("op") == "and"):
            return None
        tag0 = _match_stmt_tag_test(t0.get("left", {}), stmtv)
        if tag0 != "Return" or _match_get_call(t0.get("right", {}), stmtv) != "value":
            return None
        with_value = True
    if tag0 is None:
        return None
    if not (len(a0.get("body", [])) == 1 and _is_bool_true_return(a0["body"][0])):
        return None
    # arm 1: for key in ("body","orelse"): if key in stmt and self(stmt[key]): return True
    if not _match_field_descend_loop(a1, stmtv, names):
        return None
    # arm 2 (optional): if stmt.get("stmt")=="Match": for c in stmt.get("cases",[]): if self(c.get("body",[])): return True
    if a2 is not None and not _match_cases_descend(a2, stmtv, names):
        return None
    if not names or any(x != names[0] for x in names):
        return None
    return {"subject": subj, "self_name": names[0], "with_value": with_value, "tag": tag0}


def _match_field_descend_loop(node: Any, stmtv: str, names: List[str]) -> bool:
    """`for key in ("body","orelse"): if key in <stmt> and <self>(<stmt>[key]): return True`."""
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
    # right: self(stmt[key])
    if not _is_selfcall_1(right, names):
        return False
    arg = right["args"][0]
    if not (isinstance(arg, dict) and arg.get("type") == "Subscript"
            and _is_var(arg.get("value"), stmtv) and _is_var(arg.get("index"), keyv)):
        return False
    return len(iff.get("body", [])) == 1 and _is_bool_true_return(iff["body"][0])


def _match_cases_descend(node: Any, stmtv: str, names: List[str]) -> bool:
    """`if <stmt>.get("stmt")=="Match": for c in <stmt>.get("cases",[]):
        if <self>(c.get("body",[])): return True`."""
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
    if not _is_selfcall_1(call, names):
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
    subtree (a superset of `body`/`orelse`/`cases`)."""
    n = whyml_ident(func["name"])
    tag = desc["tag"]
    out = _emit_stmt_reader(n)
    out.append(f"  let rec {n} (stmts: list pyval) : bool")
    out.append("    requires { true } ensures { true } variant { size_list stmts }")
    out.append(f"  = match stmts with Nil -> false | Cons h t -> {n}__v h || {n} t end")
    out.append(f"  with {n}__v (v: pyval) : bool")
    out.append("    requires { true } ensures { true } variant { pv_size v }")
    out.append("  = match v with")
    out.append(f'    | PDict d -> {n}__stmt_is v "{tag}" || {n}__d d')
    out.append(f"    | PList xs -> {n} xs")
    out.append("    | _ -> false end")
    out.append(f"  with {n}__d (d: pydict) : bool")
    out.append("    requires { true } ensures { true } variant { size_dict d }")
    out.append("  = match d with DNil -> false")
    out.append(f"    | DCons _ v rest -> {n}__v v || {n}__d rest end")
    return out


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

    # ≥1 self-recursion merge `<acc>.update(self(…))`.
    if not any(_match_acc_update_self(s, acc, func["name"])
               for s in _iter_dict_nodes(lbody)):
        return None

    # exactly one ArraySet on <acc> (the runtime-keyed insert).
    sets = [s for s in _iter_dict_nodes(lbody)
            if s.get("stmt") == "ArraySet" and _is_var(s.get("array"), acc)]
    if len(sets) != 1:
        return None
    aset = sets[0]

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
    needed = [gkey, kkey]
    if value["kind"] == "str2":
        needed += [value["child_key"], value["field_key"]]
    seen: set = set()
    for key in needed:
        if key in seen:
            continue
        seen.add(key)
        out += _pv_reader_lines(n, key)

    gsuf = _reader_suffix(gkey)
    ksuf = _reader_suffix(kkey)

    # ---- the per-node pre-action: guarded runtime-keyed insert ----
    out.append(f"  let {n}__pre (d: pydict){extra_sig} : sdict")
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
