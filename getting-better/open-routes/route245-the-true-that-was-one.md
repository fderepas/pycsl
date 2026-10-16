# OPEN ROUTE #245 — IN A CONTRACT, AN hval `True` AND `1` ARE THE SAME VALUE, SO `isinstance(_, bool)` AGREES

**Status: OPEN (gen #36, 2026-10-16), Severity 1.** Recorded as a residual by the #242 repair executor;
driver-reproduced at HEAD 7b823836 (rc=0 "Verification SUCCESS").

## Witness
`witnesses-r245/hval_true_is_one_in_contract.py`: `f(d: Dict[str, PyVal])` with
`requires d["a"] == d["b"]` and `ensures isinstance(d["a"], bool) == isinstance(d["b"], bool)` PROVES. CPython:
`{"a": True, "b": 1}` satisfies the precondition (`True == 1`) and violates the postcondition.

## Mechanism
Route #237's contract-side `hval_isinst_opaque h "bool"` is a function of the hval only; `True` and `1` are
both `HInt 1`, so equal hvals give equal answers. Python equality does NOT imply equal type.

## Repair direction
Fail-closed: refuse `isinstance(<hval>, bool)` (and `type(<hval>) is bool` etc.) in contracts, or make the
contract-side answer depend on something other than the `HInt` payload. A faithful fix needs a bool
constructor in the certified hval type (Phase2f certificate change) — out of scope for a quick repair.
