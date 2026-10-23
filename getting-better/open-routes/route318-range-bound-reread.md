# OPEN ROUTE #318 — THE BOUND OF `range(<expr>)` IS RE-EVALUATED AT EVERY ITERATION (Python evaluates it once)
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 17; driver-reproduced on main f44477b7 (rc=0; CPython violates).
Witnesses `witnesses-r318/`: `n = 2; for i in range(n): n = 5; c += 1` proves `\result == 5` (CPython 2) (l41); `range(len(s))` with s
rebound in the body (l43); `range(n + 1)` (l45); shrinking bound in a nested loop (l54). Emitted loop test `while !_idx_i < <bound>`
where <bound> is `!n` / `(!n + 1)` / `(str_length_op !s)`; constant and field bounds are captured once (`let _len_idx_i = o.n`) and
correct; `range(lo, hi)` start is correct. Needs user invariants + loop variant (no automatic variant for a live bound).
Repair: capture every range argument (start, stop, step) ONCE into a fresh immutable binding before the loop, in Python order (#307), for
every bound shape; census every for-range lowering path (incl. seq-promoted lists, enumerate/zip ranges, l53 near-miss).
