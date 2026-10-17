# OPEN ROUTE #263 — RECURSION THROUGH METHOD CALLS IS NEVER CHECKED FOR TERMINATION

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 3; driver-reproduced at HEAD 13451c8d (t06/t09/h04 rc=0;
CPython RecursionError). Witnesses `witnesses-r263/`: t06 (self-recursive method), t08 (+ no_exception), t09
(mutually recursive methods), t10 (function -> method -> function cycle), h04 (`#@ happy ... total` policy proves
for a non-terminating `parse`).
Mechanism: every `self.m()`/`obj.m()` call is a bodyless `val` stub keeping the callee's `ensures` (when it has no
`requires`), so Why3 sees no cycle: a plain `let` with no variant/diverges claims termination and assumes the
callee's postcondition circularly. Top-level recursion is `let rec` and is checked. Route #206 checks only cycles
through trusted stubs.
Repair: build the full call graph including method calls (resolved by receiver class / self), and for any cycle
either require a `#@ variant`/`decreases` checked across the cycle, or mark `\diverges` / refuse; the callee's
postcondition must not be assumed within its own SCC without a termination argument.
