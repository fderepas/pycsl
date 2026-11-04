# OPEN ROUTE #559 — THE BUILTIN TYPE OBJECT `int` AS A LIST ELEMENT IS AN OPAQUE int CONSTANT, SO `ys = [int]; return ys[0] + 1` PROVES `no_exception \all` (R325 REFUSES THE DIRECT `int + 1` / `len + 1` / `range(len)` ...; `xs[int]` KEEPS ITS BOUNDS OBLIGATION) (1)
**Status: OPEN, Severity 1 (opened at the end of driver run #4; NOT repaired in run #4 — first in line for run #5).** Red-team round 53 (2026-11-04, on 3833d61d4 = main with routes through #545 and the whyml_ident conversion: 2695 probes g1400-g1446, 2531 CPython-breaching, 252 confirmed in 9 families, default mode only; typed / store 0 of 254). Census `scratchpad/rt53/census.tsv`; family block from `scratchpad/rt53/FINDINGS.txt`.
Witnesses `witnesses-r559/` (1): `g1414_do1232_int_list_elt.py`.

Driver repro on int30 (= main + #546-#555, the run's last integration), 2026-11-04T07:30Z: 9 rt53 exemplars (dh1200 df1202 dg1352 do1232 dt1200 dx1200 eb1241 ef1200 eu1200) rc=0 Verification SUCCESS while CPython breaks the claim (scratchpad/rt53/driver-repro.txt) — none is closed by the #546-#555 repairs.

```
F4 THE BUILTIN TYPE OBJECT `int` AS A LIST ELEMENT IS AN OPAQUE int CONSTANT, SO `ys = [int]; return ys[0] + 1` PROVES `no_exception \all` (R325 REFUSES THE DIRECT `int + 1` / `len + 1` / `range(len)` ...; `xs[int]` KEEPS ITS BOUNDS OBLIGATION) (1)
  EXEMPLAR: g1414/do1232_int_list_elt.py: `#@ no_exception \all` `def f(k: int, xs: List[int]) -> int: ys = [int]; return ys[0] + 1`
  CPYTHON: do1232: f(1, [1, 2]) -> TypeError: unsupported operand type(s) for +: 'type' and 'int'
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt53 && PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt53/g1414/do1232_int_list_elt.py --import-path src/pycsl  ->  rc=0 'Verification SUCCESS'
  WHY: as F1: the builtin name is an opaque int; R325 refuses most int uses of `len` / `print` / `math` (g1414) but not these two.
  PROBES: g1414/do1232_int_list_elt.py
```
