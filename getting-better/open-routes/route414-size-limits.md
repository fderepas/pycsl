# OPEN ROUTE #414 — Py_ssize_t / SIZE LIMITS ARE NOT OBLIGATIONS (the 4300-digit str(int) limit IS)
**Status: REPAIRED (candidate, g2 run #3), Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
Witnesses `witnesses-r414/`: `i03_len_range_huge.py`, `i04_str_mul_huge.py`, `i19_list_mul_huge.py`, `i06_lshift_huge.py`.

```
#414 Py_ssize_t / SIZE LIMITS ARE NOT OBLIGATIONS (the 4300-digit str(int) limit IS)  [old family; platform limits]
  i03  len(range(n)), requires n >= 0, f(10**20)                                               OverflowError
  i04  "a" * n;  i19  [0] * n;  i06  1 << n (f(2**64))                                          OverflowError
  WhyML: `iter_length (py_range_1 n)`, `str_repeat_op "a" n`, `Array.make n 0`, `bit_lshift 1 n` with no bound.
  (str(n) / f"{n}" / print(n) carry the -10**4300 < n < 10**4300 assert and fail -- i05, i12, i21.)
  REPAIR: `n < 2**63` (sys.maxsize) obligations at len(range), sequence repetition, Array.make, and a shift-count
  bound at <<, as was done for the digit limit.
```

## REPAIR (2026-10-26, g2 executor off 4431ef86f; docs annotations §7.72 / translational §T.6.83)
**Decision: Py_ssize_t OVERFLOW obligations, consistent with the 4300-digit row; NO memory-cap assumption.** The
OverflowError of each site is a fixed platform bound (sys.maxsize = 2**63 - 1, 64-bit), exactly like route #281's
`|x| < 10**4300`, so it is an obligation, under `no_exception \all` only (OverflowError is not Phase 1; route #332's rule):
`len(range(stop))` owes `stop <= S`; `range(start, stop)`: `stop - start <= S`; `range(a, b, step)`: `|b - a| <= S`;
str `s * n` owes `-2**63 <= n <= S /\ (n <= 0 \/ len(s) * n <= S)` (index conversion, then "repeated string is too long",
new witness 6067); `[x] * n` owes `n <= S` (`Array.make` already owes `n >= 0`); `x << n` owes `x = 0 \/ n <= S`
(`0 << 2**70` is fine in CPython). Each obligation wraps the size operand (the term keeps its head).
MemoryError BELOW these bounds (`"a" * 2**40`, `[0, 0] * 2**62`, `1 << 2**40`) is NOT modelled. Declaring a memory cap
would be a NEW declared assumption in the ledger: left to the user (see the open decision below), as is
RecursionError's (route #269).
Measured together on the final candidate (g2 worktree off 4431ef86f; base = the official `bin/byte-diff-sweep.sh` at 4431ef86f
from the clean g1-base tree, cwd = tree root; candidate the same script from the g2 tree): root 2441 -> 2455 .mlw, 2 MOVED
(`1163`, `1164`: #414's shift obligation), 1 GONE (`3269`, #415), 0 APPEARED, 15 new emitting sources (the 20 new witnesses /
controls minus the 5 refused); pyref 2186 -> 2186, 1 MOVED (`0110`: #412's `no_div_zero (0)` inside a `try/except
ZeroDivisionError`, exactly the assert `//` already gets there), 0 GONE, 0 APPEARED; mirrors 53/53, 0 MOVED / 0 GONE / 0
APPEARED. M1 re-proofs base -> candidate: `1163` FAIL -> FAIL (expected FAIL), `1164` PROVED -> PROVED, `3269` FAIL -> REFUSED
(expected FAIL), pyref `0110` FAIL -> FAIL (a pre-existing real/int type error at both).
Movers of this route alone: `1163`, `1164` (the `<<` obligation: on `1 << -1` after the ValueError row, and on a folded
`1 << 3`). Over-refusal: none (no refusal is added).
Witnesses PROVED rc=0 at base -> FAIL rc=1: 6063 (i03), 6064 (i04), 6065 (i19), 6066 (i06), 6067 (`"ab" * n`, n < 2**63).
Control 6068 (bounded `len(range(n))`, `len(range(a, b))`, `"ab" * n`, `[0] * n`, `1 << n`, and `0 << m`): PROVED at base and
candidate.
OPEN DECISION (user): MemoryError -- a declared resource-limit assumption (like the undeclared RecursionError scope note),
or nothing. Residuals found while probing (driver-unreproduced, NOT repaired, candidate new routes): `list(range(n))` /
`sorted(range(n))` raise the same OverflowError for n > S and carry no obligation (`list_new (py_range_1 n)`);
`(1,) * n` lowers to the INT product `(1) * n` and `[1, 2] * 3` to `Array.make 3 1` (length 3, CPython 6): two wrong
lowerings of sequence repetition (emission of probe `p414_forms.py`; not proved here).
