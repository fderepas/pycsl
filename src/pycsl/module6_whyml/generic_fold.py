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
    return {"guard_key": gkey, "guard_val": gval, "add_key": akey}


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


def _match_self_recursion(stmt: Any, acc: str, fname: str) -> bool:
    """`<self>(<value_var>, <acc>)` as an ExprStmt, where `<self>` resolves to
    this same function (module-level bare name or class-qualified static call)."""
    if not (isinstance(stmt, dict) and stmt.get("stmt") == "Expr"):
        return False
    call = stmt.get("value", {})
    if not (isinstance(call, dict) and call.get("type") == "Call"):
        return False
    cf = call.get("func")
    if not isinstance(cf, str) or _canon_call(cf) != fname:
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
    if pre is not None:
        for role, key in (("guard", pre["guard_key"]), ("add", pre["add_key"])):
            ctor = _irkey_ctor(key)
            rname = f"{n}__get_{_reader_suffix(key)}"
            if rname in reader_names.values():
                continue
            reader_names[key] = rname
            out.append(f"  let rec {rname} (d: pydict) : option pyval")
            out.append("    variant { d }")
            out.append("  = match d with")
            out.append("    | DNil -> None")
            out.append(f"    | DCons {ctor} v _ -> Some v")
            out.append(f"    | DCons _ _ rest -> {rname} rest")
            out.append("    end")

    # ---- inlined pre-action ----
    if pre is not None:
        gname = reader_names[pre["guard_key"]]
        aname = reader_names[pre["add_key"]]
        out.append(f"  let {n}__pre (d: pydict) ({acc}: {acc_ty}) : unit")
        out.append(f"    writes {{ {acc} }}")
        out.append(f"  = match {gname} d with")
        out.append("    | Some (PStr s) ->")
        out.append(f'        if pystr_eq s "{pre["guard_val"]}" then')
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
