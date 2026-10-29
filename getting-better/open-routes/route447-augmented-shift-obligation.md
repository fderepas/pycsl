# OPEN ROUTE #447 — AUGMENTED shift `c <<= b` / `c >>= b` on a local or parameter skips the BinOp shift obligation (ValueError / OverflowError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r447/` (13): `c1_o028_aug_lshift_neg.py`, `c11_q060_realistic_mask.py`, `c11_q063_aug_shift_param.py`, `c11_q064_aug_rshift_param.py`, `c11_q065_aug_shift_huge.py`, `c31_a003_annot.py`, `c31_a013_param.py`, `c31_a004_annot.py`, `c31_a014_param.py`, `c4_a000_aug_ll.py`, `c4_a001_aug_rr.py`, `c4_a006_aug_ll.py`, `c5_x003_lshift_lit_rhs.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F4 -- AUGMENTED shift `c <<= b` / `c >>= b` on a local or parameter skips the BinOp shift obligation (ValueError / OverflowError)   (13)
  EXEMPLAR c11/q060_realistic_mask.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(width: int) -> int:
    |     mask = 1
    |     mask <<= width
    |     return mask - 1
    CPython 3.14: f(-1)  ->  VIOLATION ValueError negative shift count
  MECHANISM: `c <<= b` lowers to `a := (bit_lshift !a b)` (mlw/o028) WITHOUT the `b >= 0` (and ssize_t) obligation that the
  expression `a << b` gets (AugAssign maps `<<` to `bit_lshift` directly, statements.py:3256-3258, while the
  BinOp path wraps it in `_wrap_with_no_exception_assert`, expressions.py:7385-7402; c1/o013 `return a << b` is NOT proved: 8 Unknown). Field / element targets do get it
  (a020 Unknown, a040 type error); only a Name target (local or parameter) skips it.
  REPAIR: Lower every AugAssign `t op= e` through the SAME BinOp path (`t = t op e`, including its obligations) for every
  operator; a census of AugAssign lowering per (target kind x operator) must match the BinOp obligation table
  (shifts: count >= 0 and < ssize_t bound; // % : divisor != 0; ** : 0 ** negative).
  MEMBERS: c1/o028_aug_lshift_neg.py c11/q060_realistic_mask.py c11/q063_aug_shift_param.py c11/q064_aug_rshift_param.py c11/q065_aug_shift_huge.py c31/a003_annot.py c31/a013_param.py c31/a004_annot.py c31/a014_param.py c4/a000_aug_ll.py c4/a001_aug_rr.py c4/a006_aug_ll.py c5/x003_lshift_lit_rhs.py
```
