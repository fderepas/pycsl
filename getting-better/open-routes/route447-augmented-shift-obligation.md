# OPEN ROUTE #447 — AUGMENTED shift `c <<= b` / `c >>= b` on a local or parameter skips the BinOp shift obligation (ValueError / OverflowError)
**Status: REPAIRED (executor r3, driver run #3, 2026-10-29), Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
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

## REPAIR (executor r3, driver run #3, 2026-10-29, off db6c57253; annotations §7.200, translational §T.6.210)

Code inline in `_handle_augassign_stmt` (src/pycsl/module6_whyml/statements.py; its mirror twin is `\trusted`, no new
def, no axiom). An augmented SHIFT `c <<= b` / `c >>= b` on a NAME target is lowered as the expression `c << b` / `c >> b`
(an IR `BinOp` over `Var c`, through `_expr_to_whyml` -> `_handle_binop`), so it carries exactly the expression's
obligations: `non_neg_shift (b)` (`("binop", "<<"/">>")`, ValueError) and, for `<<` under `\all`, route #414's
`!c = 0 \/ b <= 9223372036854775807` (OverflowError). AUDIT of every augmented operator on a name target against its plain
BinOp row: `//=` (IR `div`), `%=`, `/=` were an ill-formed `c := !c div b` (refused by Why3 only by an accident of syntax;
the floored `pycsl_div` / `pycsl_mod` preamble is scanned from BinOp sites only, so routing them would have needed a
mirrored `ir_scanner` change) -- now REFUSED, `PYCSL-R447-AUGASSIGN-DIVISION` ("write `c = c // b`"); `**=` keeps #259's
`requires { y >= 0 }` on `py_pow` (excludes `0 ** -n`, its ZeroDivisionError row); `+ - * & | ^` have no row; `@=` is
route #446's. Field / element targets already go through their own paths (rt36 a020-a049: not proved / refused).
Witnesses 7000-7005 (6 of the 13 red-team probes; all 13 PROVED at base 8fe7204c3 and all 13 now FAIL: the
shift obligation is Unknown), 7006 / 7007 (`//=` / `%=`, REFUSED; a type error at base). Controls 7008 (`c <<= b; c >>= b`
under `0 <= b < 64`) and 7009 (the advice: `c = c // b` under `b > 0`, `\result == a // b`): PROVED at base and candidate.
Corpus / mirror: no augmented shift or division on a name exists outside the new files, so 0 MOVED.

GATES (one candidate, one battery for #447 / #451 / #452 / #454 / #456 / #459; see the README run-#3 r3 entry): fidelity sync / mirror-check rc=0; root corpus 2569 base -> 2581 candidate .mlw, 0 MOVED, 3 GONE (5066 / 5071 / 5072, expected FAIL route-#375 witnesses `[*self]` / `(*self,)` / `g(*self)` on a field-less class: VERIFY-FAIL -> REFUSED by #454), 0 APPEARED; pyref 2186 / 2186 0 / 0 / 0; mirror 53 / 53 0 / 0 / 0 (no OWED proof); planes / ledgers: see the README entry.

## RESIDUALS: no fail-closed site census for the shift row (a lowering that bypassed `_handle_augassign_stmt` -- a
recognised fold -- would drop it; measured: the `while` shape q061 keeps the assertion); `//=` / `%=` / `/=` on a name are
refused rather than supported.
