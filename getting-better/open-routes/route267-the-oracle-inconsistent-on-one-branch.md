# OPEN ROUTE #267 — THE NON-VACUITY GATE MISSES AN INCONSISTENCY REACHED ON ONLY ONE BRANCH

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 2 (rests on a user-written unsatisfiable `\abstract` contract).**
Red-team round 3; driver-reproduced at HEAD 13451c8d (rc=0; CPython 2). Witness `witnesses-r267/a04_abstract_branch_vacuous.py`:
`\abstract oracle(x)` with `ensures x != 5` (false at x = 5) called only under `if x == 5:`; the branch then returns 2
while the claim is `\result == 1` — the branch is dead in the model. All-path inconsistencies are caught (a01/a03).
Repair: the vacuity gate should check reachability per branch/call site (e.g. assert-false probes after each abstract
call, flagged when provable), or check abstract contracts for satisfiability over their full domain.

## Probe table (283d1033 = base)
| file | shape | base | after |
|---|---|---|---|
| 2821 (a04) | `\abstract` `ensures x != 5` called under `if x == 5:`, claim `\result == 1` (CPython 2) | PROVED | VACUOUS (FAIL) |
| 2822 | `\trusted` with contradictory `ensures \result > x` / `< x`, called for x > 0 (CPython 5) | PROVED | VACUOUS (FAIL) |
| 2823 control | honest `\trusted` callee on one branch | PROVED | PROVED |
| 2824 control | branch dead BEFORE the call (`requires x > 10`, `if x == 5:`) calling a `\trusted` callee | PROVED | PROVED |

## Repair (gen #36, 2026-10-17)
Inline in `pycsl.py:_run_vacuity_gate` (per probed function, before the all-exits probe). The audited
callees are the emitted `val`s with an `ensures` and none of `raises` / `diverges` / `ensures { false }`
(a callee that may raise or diverge, or is `-> NoReturn`, legitimately has a dead normal continuation).
Such a callee must return, so its `ensures` must be satisfiable wherever it is called. Each outermost call
`(f ...)` to one in the function body (outside `{ ... }` spec braces) is rewritten
`(check {false}; let r = (f ...) in check {false}; r)` — `check` adds no hypothesis — and the function is
flagged VACUOUS iff the AFTER check proves (any prover) while the BEFORE check does not. A deadness the
program already had before the call (defensive code, dead-by-design consequence branches) is NOT flagged:
the gate's documented ALL-exits philosophy is kept for program-induced deadness, and only
callee-contract-INDUCED deadness fails, with the existing VACUOUS reporting (the name carries
`[the call to `f` makes its continuation unreachable ...]`). A probe file why3 rejects is reported
(`[!] vacuity call-site probe ... could not be checked`), not passed silently.

Cost (measured over the emitted corpus, call-site probes only, all-exits probe short-circuited): root 383
files / 538 sites -> 1067 prover-goal attempts; pyref 27 files / 36 sites -> 71; i.e. one extra `check`
goal per audited call site per prover, plus one per site whose AFTER check proves. Mirror: 38 files /
1752 sites; the 17 smaller files measured (421 attempts, 0 flags); the remaining small and the seven big
files (expressions/statements/stmt_control_flow/functions/Transpiler/Module5_IREmitter/pure_ast) OWED.
False positives: 0 among non-failing files. The measurement flagged 5 files, all `# pycsl-expected: FAIL`
broken-class-invariant witnesses (1561/1564/1565 route #165, 2735/2736 route #261) whose post-call context
assumes the type invariant the pre-call state violates; they FAIL before the gate at base and after
(re-proved), so no verdict moves. Emission is untouched (byte-diff 0 MOVED everywhere).

Residuals: callees declared in another Why3 module (`use`d stdlib stubs) are not audited (their stubs are
body-verified by policy); nested calls `(f (g x))` audit only the outermost; a call inside a record/brace
expression is skipped; abstract contracts unsatisfiable only under a `raises` arm are exempt by design.
