# OPEN ROUTE #498 — `is` / `is not` BETWEEN TWO FRESHLY COMPUTED int OR str VALUES IS DECIDED AS VALUE EQUALITY (`(n + 1) is (n + 1)`, `s + "x" is s + "x"`, `s[0:2] is s[0:2]`, `s.upper() is s.upper()`): ROUTE #42's WHITELIST COVERS ONLY THE bool-LITERAL OPERAND
**Status: REPAIRED (executor u4, driver run #4, 2026-11-01, off 5a9e2e161; see REPAIR below), Severity 1.** Red-team round 44 (driver run #4, 2026-11-01, on 1c30f94b3 = main: 793 probes in g500-g527, 779 CPython-breaching, 139 confirmed (probe, mode) pairs on 111 probes in 5 families). Census `scratchpad/rt44/census.tsv`; the family block below is quoted from `scratchpad/rt44/FINDINGS.txt`.
Witnesses `witnesses-r498/` (14): `g505_n50500_is_bigint_runtime.py`, `g505_n50503_is_str_concat.py`, `g515_j51500_int_add_same.py`, `g515_j51501_int_isnot_add.py`, `g515_j51502_int_mul_vs_add.py`, `g515_j51505_int_branch.py`, `g515_j51506_int_local_alias_arith.py`, `g515_j51510_neg_int_is.py`, `g515_j51512_str_concat_is.py`, `g515_j51513_str_concat_isnot.py`, `g515_j51514_str_slice_is.py`, `g515_j51515_str_upper_is.py`, `g515_j51519_str_join_is.py`, `g521_k52110_int_is_ne_guard_div.py`.

Driver repro: session scratchpad `rp44/repro.sh` on 1217d2745 (main's code), 2026-11-01T02:20Z: all 12 rt44 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F3 `is` / `is not` BETWEEN TWO FRESHLY COMPUTED int OR str VALUES IS DECIDED AS VALUE EQUALITY (`(n + 1) is (n + 1)`, `s + "x" is s + "x"`, `s[0:2] is s[0:2]`, `s.upper() is s.upper()`): ROUTE #42's WHITELIST COVERS ONLY THE bool-LITERAL OPERAND (14)
  EXEMPLAR: g515/j51500_int_add_same.py: `#@ ensures \result == True` f(n): `return (n + 1) is (n + 1)`
  CPYTHON: f(1000) -> False (VIOLATION contract False)
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt44 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt44/g515/j51500_int_add_same.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt44/g515 && /home/fabrice/git/pycsl-rt44/.venv/bin/python3 -E -s j51500_int_add_same.py)
  WHY: src/pycsl/frontend/Module5_IREmitter.py:8236-8240 narrows every `is`/`is not` to `==`/`!=` (+ `py_is` marker); src/pycsl/module6_whyml/expressions.py:22105ff reads the marker only when one operand is a Bool literal, so an int/str identity test lowers as Why3 `=` on the values. REPAIR: an `is` whose operands are not both singletons (None/True/False/Ellipsis) or the same variable is an uninterpreted predicate (or refused).
  PROBES: g505/n50500_is_bigint_runtime.py g505/n50503_is_str_concat.py g515/j51500_int_add_same.py g515/j51501_int_isnot_add.py g515/j51502_int_mul_vs_add.py g515/j51505_int_branch.py g515/j51506_int_local_alias_arith.py g515/j51510_neg_int_is.py g515/j51512_str_concat_is.py g515/j51513_str_concat_isnot.py g515/j51514_str_slice_is.py g515/j51515_str_upper_is.py g515/j51519_str_join_is.py g521/k52110_int_is_ne_guard_div.py
```

## REPAIR (executor u4, driver run #4, 2026-11-01; annotations §7.498)

Inline in `pycsl.py::_run_pipeline` before Module 6 (mirror twin `\trusted`; no new def, no axiom; Module 5's narrowing and
routes #42 / #52 untouched), new code `PYCSL-R498-IS-ON-FRESH-VALUE`, refuse by default over every function and class
declaration of the IR: an `is` / `is not` that is not against a singleton (None / Ellipsis / NotImplemented; a bool literal
stays #42's), not of one name with itself or with a chain of single plain assignments of it (`y = x; z = y; z is x`), and
not one #52 refuses, is REFUSED when either operand MAY BE FRESH -- an arithmetic / bitwise / concatenating operator, unary
`-` / `+` / `~`, a slice, an f-string, a display / comprehension / lambda / literal, any call but `type` / `isinstance` /
`issubclass` / `hasattr` / `callable` / `bool`, an index of a str / bytes or of a fresh receiver, a fresh arm of an
if-expression / `and` / `or`, a parameter without a class annotation, and a local bound by anything but plain assignments
of non-fresh values (loop / unpacking / `with` / `except` / walrus / augmented bindings count as fresh).


Witnesses: all 14 in `witnesses-r498/` REFUSED (`PYCSL-R498-IS-ON-FRESH-VALUE`) under default, `--memory-model typed` and
`--memory-model store` (42/42 runs). Corpus 7900-7907 (PROVED at base, REFUSED), 7908 (`object` parameters: NOT PROVED at base,
refused by the parameter arm), 7909 (store: Why3 type error at base, refused by name); controls 7915 (an alias chain over an
enum member) / 7916 (`c.a is c.a`) PROVED. Advice followed: `==` (a498_write_eq) and an alias identity VERIFY.
Over-refusal: corpus root 0 MOVED, GONE only 2391 (an expected-FAIL `x is not y` on `Any` parameters, now refused by the
parameter arm) and 0642 (route #499); pyref 2186/2186 0/0/0; mirror 53/53 0/0/0 (a first draft that judged the import
closure's merged IR refused 5 mirror files -- fixed in e55311cf0 by judging only the claimed file's own functions / classes).
rt43 / rt44 CPython-honest controls (37): one newly refused, rt44 k52114 (`a = 10 ** 30; b = 10 ** 30; a is b`, True in CPython
only through constant folding) -- refused by design. Named residuals: a field / module global STORING a computed int / str
(`self.a is self.b`) is read as an existing object; a list / dict element read by index is fresh only through its receiver.
Commits: e51cc4600 (rule + corpus), e55311cf0 (own-file scope; control / witness adjustments).
