# OPEN ROUTE #237 — `isinstance(<hval>, dict)` IS THE CONSTANT `true`

**Status: OPEN (gen #36, 2026-10-15), Severity 1.** Found by the ch12 chain agent (asked to check exactly this
before building an hval seam); driver-reproduced at HEAD 0923aa92: both witnesses rc=0 "Verification SUCCESS".

## Witnesses (PROVED at HEAD)
- `witnesses-r237/isinst_dict.py`: `x = d.get("k", {})` on `d: Dict[str, PyVal]`; `if isinstance(x, dict): return 1`
  / `return 0` with `ensures \result == 1`. CPython `f({"k": "s"})` = 0.
- `witnesses-r237/notdict.py`: the negated form; CPython `h({"k": 5})` = 0.
Emission: `if true then raise (Return 1) ...`.

## Mechanism
`src/pycsl/module6_whyml/expressions.py` ~L11396 (the "union/match cluster" isinstance branch, 38a46208):
an hval subject "IS a Python dict" — false: an hval is `HStr | HInt | HArr | HNode | HMap ...`. Any
`x = d.get(...)` on a `Dict[str, PyVal]` is a pyval local, so ordinary user code reaches it.

## Repair direction
Lower `isinstance(<hval>, dict)` to a constructor test (`match x with HMap _ -> true | _ -> false end`), and
`isinstance(<hval>, str|int|list)` likewise, or opaque — never a constant. Note the missing-key default
`d.get("k", {})` is emitted `HInt 0` (should be the empty map) — becomes observable once isinstance is
faithful. Mirror impact: `stmt_control_flow::_match_subject_union_info` uses `not isinstance(subj, dict)`
(ensures True) -> owes a whole-file re-proof. Agent's axiom-free spike: ch12 scratch `mlwspike/hval_isinst_streq.mlw`.
