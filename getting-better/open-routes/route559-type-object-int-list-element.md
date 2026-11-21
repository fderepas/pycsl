# OPEN ROUTE #559 — THE BUILTIN TYPE OBJECT `int` AS A LIST ELEMENT IS AN OPAQUE int CONSTANT, SO `ys = [int]; return ys[0] + 1` PROVES `no_exception \all` (R325 REFUSES THE DIRECT `int + 1` / `len + 1` / `range(len)` ...; `xs[int]` KEEPS ITS BOUNDS OBLIGATION) (1)
**Status: REPAIRED (run #4, executor u24 off fb3880c2a (int30 79ce685c7 + the #556-#564 route docs), commit 48de7b7ab + its ledger / docs commit). Mechanism (inline in `_run_pipeline` after route #552's judge, on the §7.541 kinds, own scope of every judged body; mirror twin `\trusted`, lambdas only, no new def, no axiom, emitter untouched; annotations §7.557): `PYCSL-R559-BUILTIN-OBJECT-ELEMENT` -- a builtin function / type object not bound by the file as a list / set / tuple display element, a dict display value or an `append` / `add` / `insert` argument; a classinfo tuple of `isinstance` / `issubclass`, an `except` tuple, a typing form (annotation / subscript slice) and an equality / identity / membership-only comparand are not values. Witnesses `witnesses-r559/` x default / typed / store: 1 x 3 = 3/3 REFUSED; corpus 8746 FAIL, control 8771 PASS (base and HEAD). Over-refusal: corpus 0 honest files newly refused (root GONE 2: 1679 / 1680, expected FAIL, an int into an `Optional[Tok]` method parameter, now R563); python-reference 0; rt43 / rt44 149 honest controls 0 newly refused; mirror 53/53 0 MOVED / 0 GONE.**
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
