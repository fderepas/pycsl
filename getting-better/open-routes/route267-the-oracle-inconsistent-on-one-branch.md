# OPEN ROUTE #267 — THE NON-VACUITY GATE MISSES AN INCONSISTENCY REACHED ON ONLY ONE BRANCH

**Status: OPEN (gen #36, 2026-10-17), Severity 2 (rests on a user-written unsatisfiable `\abstract` contract).**
Red-team round 3; driver-reproduced at HEAD 13451c8d (rc=0; CPython 2). Witness `witnesses-r267/a04_abstract_branch_vacuous.py`:
`\abstract oracle(x)` with `ensures x != 5` (false at x = 5) called only under `if x == 5:`; the branch then returns 2
while the claim is `\result == 1` — the branch is dead in the model. All-path inconsistencies are caught (a01/a03).
Repair: the vacuity gate should check reachability per branch/call site (e.g. assert-false probes after each abstract
call, flagged when provable), or check abstract contracts for satisfiability over their full domain.
