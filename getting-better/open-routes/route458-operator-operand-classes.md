# OPEN ROUTE #458 — binary operator on MISMATCHED builtin classes lowered by one operand's class: `str / str` -> path join, `int + str` / `bool + str` -> str_concat (TypeError)
**Status: OPEN, Severity 1.** Red-team round 36 (2026-10-29, SYSTEMATIC census of operators / dunders / scoping / call binding / modules after #440-#443 on 8fe7204c3: 1723 probes all fully proved / 240 proved / 209 confirmed; rt35's 175 all closed). Census TSV `scratchpad/rt36/census.tsv`; the family block below is quoted from `scratchpad/rt36/FINDINGS.txt`.
Witnesses `witnesses-r458/` (19): `c27_o003.py`, `c27_o010.py`, `c29_o000.py`, `c29_o004.py`, `c29_o010.py`, `c29_o016.py`, `c29_o023.py`, `c29_r000_realistic_path.py`, `c29_r003_concat_ensures.py`, `c31_o007.py`, `c31_o008.py`, `c37_o002.py`, `c37_o003.py`, `c37_o004.py`, `c37_o008.py`, `c37_o009.py`, `c37_o011.py`, `c37_o012.py`, `c37_o013.py`.

Driver repro: 16/16 family exemplars rc=0 Verification SUCCESS on main 8fe7204c3 at 2026-10-29T02:35Z, each violating under CPython (scratchpad/rt36/driver-repro.txt).

```
FAMILY F15 -- binary operator on MISMATCHED builtin classes lowered by one operand's class: `str / str` -> path join, `int + str` / `bool + str` -> str_concat (TypeError)   (19)
  EXEMPLAR c29/r000_realistic_path.py  PROVED (rc=0 Verification SUCCESS):
    | #@ no_exception \all
    | def f(base: str, name: str) -> int:
    |     full = base / name
    |     return len(full)
    CPython 3.14: f('/etc', 'hosts')  ->  VIOLATION TypeError unsupported operand type(s) for /: 'str' and 'str'
  MECHANISM: The BinOp lowering picks an implementation from ONE operand's class without checking the pair: `s / t` with
  two str operands lowers to `path_join_op s t` (the pathlib `Path / str` model, mlw/o003) and `n + s` (int + str)
  lowers to `str_concat n (str_hash_op s)` (mlw/o010); `True + s` likewise. CPython raises TypeError for all.
  Other mismatched pairs are refused (#441: `s / n`, `s - n`, `s + n`, `xs + n`) or fail to type-check (c27 / c29).
  REPAIR: ALLOW-LIST of (operator, left class, right class) triples -- the CPython numeric tower (int/bool/float), sequence
  concat / repeat (str+str, list+list, tuple+tuple, bytes+bytes, seq*int, int*seq), set and dict operators, and
  `/` only with a pathlib.Path operand -- every other pair is refused under no_exception (TypeError); the str
  concat and path-join lowerings must assert both operand classes.
  MEMBERS: c27/o003.py c27/o010.py c29/o000.py c29/o004.py c29/o010.py c29/o016.py c29/o023.py c29/r000_realistic_path.py c29/r003_concat_ensures.py c31/o007.py c31/o008.py c37/o002.py c37/o003.py c37/o004.py c37/o008.py c37/o009.py c37/o011.py c37/o012.py c37/o013.py
```
