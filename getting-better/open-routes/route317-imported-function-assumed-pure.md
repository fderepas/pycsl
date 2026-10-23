# OPEN ROUTE #317 — AN IMPORTED FUNCTION/METHOD WITHOUT A CONTRACT IS ASSUMED TO WRITE NOTHING (an invented frame, never checked)
**Status: OPEN (gen #37, 2026-10-23), Severity 2 (trust boundary).** Red-team round 16; driver-reproduced on main eb75cbcf (o01 rc=0; CPython violates).
Witnesses `witnesses-r317/`: `from rt16helper import poke` where `poke(xs)` does `xs[0] = 5` with NO contract (o01); imported class method
(o03). Imports lower to `val poke (xs: array int) : unit` with no `writes`; the helper module itself proves rc=0 alone (its default frame
is not stated), yet the combined program is false. annotations.md says imported functions are "trusted stubs (contracts assumed)" —
but here no contract was written: the frame `writes nothing` is invented. With an explicit `assigns \nothing` the helper fails to
type-check (q01), so honest contracts are safe.
Repair: an imported callee with no `assigns` must get the same default frame as a local function (inferred from its verified body, or
`writes` every mutable argument), or the call is refused; document the default frame of imported stubs.
