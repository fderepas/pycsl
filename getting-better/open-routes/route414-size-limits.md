# OPEN ROUTE #414 — Py_ssize_t / SIZE LIMITS ARE NOT OBLIGATIONS (the 4300-digit str(int) limit IS)
**Status: OPEN, Severity 1.** Red-team round 32 (2026-10-26, probes around the allow-list repairs #392-#402 + R5-str); driver-reproduced on 085ee3dcc (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt32/driver-repro.txt`).
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
