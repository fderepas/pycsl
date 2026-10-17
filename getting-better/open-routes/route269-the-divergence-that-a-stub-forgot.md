# OPEN ROUTE #269 — RESIDUAL DIVERGENCE LEAKS AFTER #263

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Residuals recorded by the #263 executor; driver-reproduced
at HEAD dc693d5c (all four witnesses rc=0).

## Witnesses (`witnesses-r269/`)
- R1 `r1_receiver_form_diverging_callee.py`: terminating `m` does `C().spin(k); return 7` with `spin` `\diverges`;
  `\result == 7` PROVES (CPython never returns). The `C().m()` call form gets a generic stub `spin_1` without
  `diverges`.
- R3 `r3_comprehension_vanished_call.py`: `[self.spin(x) for x in xs]` lowers into an opaque `list_comp_int`; the
  diverging call carries no termination obligation.
- R4 `r4_diverges_no_exception.py` / `r4b_toplevel_diverges_no_exception.py`: `\diverges` + `no_exception \all` on
  unbounded recursion proves; CPython raises RecursionError (`\all` covers the five known exceptions only) —
  needs an explicit scope statement or RecursionError modelling.
- R2 (mirror, not a witness here): nine Module 5 bespoke handlers call the `\diverges` dispatcher through the fixed
  terminating stub `val self__py_expr_to_ir_1` (abstract_ops._SELF_DISPATCH_VAL_DECLS) and claim termination.
- R5: cross-module cycles are not tracked (imported receivers resolve to no edge).
## Repair direction
Every stub of a `\diverges` callee carries `diverges` regardless of call form (R1, R2); a call hidden in an opaque
comprehension must propagate its callee's divergence/raises (or be refused) (R3); R4: either model RecursionError
for unbounded recursion under `no_exception \all` (refuse `\diverges` + `no_exception \all`) or document the scope;
R5: refuse unresolvable cross-module recursion or treat imported receivers conservatively.
