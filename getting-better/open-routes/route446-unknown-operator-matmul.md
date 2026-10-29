# OPEN ROUTE #446 — unknown binary operator `@` / `@=` lowered as `unknown_op` with no raises (TypeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r446/` (7): `c1_o048_matmul.py`, `c11_q042_matmul_field.py`, `c11_q044_matmul_bool.py`, `c27_o026.py`, `c4_a047_augelem_7.py`, `c4_a074_matmul_user.py`, `c5_x001_matmul_in_cond.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F3 -- unknown binary operator `@` / `@=` lowered as `unknown_op` with no raises (TypeError)   (7)
  EXEMPLAR c1/o048_matmul.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(a: int, b: int) -> int:
    |     return a @ b
    CPython 3.14: f(1, 2)  ->  VIOLATION TypeError unsupported operand type(s) for @: 'int' and 'int'
  MECHANISM: `a @ b` lowers to `(unknown_op a b)` declared `val unknown_op (x: int) (y: int) : int` -- no raises, no precondition
  (ast.MatMult is the ONLY operator missing from the IR map _PY_OP_MAP, frontend/Module5_IREmitter.py:2078-2095,
  so it becomes `?`, which expressions.py:7403-7405 lowers to `unknown_op`; mlw/o048). `@=`, `@` on bool / field / user class (no __matmul__) are the same.
  REPAIR: ALLOW-LIST of (operator, operand class pair): an operator with no lowering rule for its operand classes is
  REFUSED under no_exception (TypeError), never lowered to `unknown_op`. `@` on int / bool / float / str / list has
  no row; on a file class only when the class (MRO) defines __matmul__ / __rmatmul__ (then its contract speaks).
  MEMBERS: c1/o048_matmul.py c11/q042_matmul_field.py c11/q044_matmul_bool.py c27/o026.py c4/a047_augelem_7.py c4/a074_matmul_user.py c5/x001_matmul_in_cond.py
```
