# OPEN ROUTE #497 — \abstract ON A FUNCTION WITH AN EXECUTABLE BODY (`return 2`, `pass`, `...` -- which return None) IS AN UNCHECKED AXIOM: THE CONTRACT IS TAKEN AS THE DEFINITION WHILE CPYTHON RUNS THE BODY (THE DOC CALLS \abstract SOUND AND NOT TRUST; THE STUB LINT DOES NOT FLAG IT)
**Status: OPEN, Severity 1 (claimed; possibly a POLICY item, see below).** Red-team round 44 (driver run #4, 2026-11-01, on 1c30f94b3 = main: 793 probes in g500-g527, 779 CPython-breaching, 139 confirmed (probe, mode) pairs on 111 probes in 5 families). Census `scratchpad/rt44/census.tsv`; the family block below is quoted from `scratchpad/rt44/FINDINGS.txt`.
Witnesses `witnesses-r497/` (4): `g509_x50900_abstract_with_body.py`, `g509_x50901_abstract_ellipsis_none.py`, `g509_x50902_abstract_ellipsis_ne.py`, `g509_x50904_abstract_pass_body.py`.

Driver repro: session scratchpad `rp44/repro.sh` on 1217d2745 (main's code), 2026-11-01T02:20Z: all 12 rt44 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F2 \abstract ON A FUNCTION WITH AN EXECUTABLE BODY (`return 2`, `pass`, `...` -- which return None) IS AN UNCHECKED AXIOM: THE CONTRACT IS TAKEN AS THE DEFINITION WHILE CPYTHON RUNS THE BODY (THE DOC CALLS \abstract SOUND AND NOT TRUST; THE STUB LINT DOES NOT FLAG IT) (12)
  EXEMPLAR: g509/x50900_abstract_with_body.py: `#@ \abstract #@ ensures \result == 1` g(): `return 2`; f: `return g()` with `ensures \result == 1`
  CPYTHON: f(0) -> 2 (VIOLATION contract 2); x50902 (`...` body, f: `g() + 1` under no_exception \all) -> TypeError
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt44 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt44/g509/x50900_abstract_with_body.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt44/g509 && /home/fabrice/git/pycsl-rt44/.venv/bin/python3 -E -s x50900_abstract_with_body.py)
  WHY: annotations.md §2.1.14: \abstract emits a bodyless `val` and 'Does not count as \trusted'; nothing requires the Python function to be absent / never called. PROVED in hoare, typed and store. REPAIR: refuse \abstract on a def that verified code calls at runtime (or treat it as \trusted for the trust lint and the soundness report). NOTE: arguably policy-level (user-authored contract); counted because the documented claim is soundness.
  PROBES: g509/x50900_abstract_with_body.py g509@typed/x50900_abstract_with_body.py g509@store/x50900_abstract_with_body.py g509/x50901_abstract_ellipsis_none.py g509@typed/x50901_abstract_ellipsis_none.py g509@store/x50901_abstract_ellipsis_none.py g509/x50902_abstract_ellipsis_ne.py g509@typed/x50902_abstract_ellipsis_ne.py g509@store/x50902_abstract_ellipsis_ne.py g509/x50904_abstract_pass_body.py g509@typed/x50904_abstract_pass_body.py g509@store/x50904_abstract_pass_body.py
```

**Policy note (driver).** `\abstract` is documented (annotations.md §2.1.14) as sound and "not trust", while the
contract of an `\abstract` function with an EXECUTABLE body is assumed and the body CPython runs is ignored. Either
the documentation and the TCB accounting are wrong (it IS trust: count it), or the directive must be refused on a
function whose body executes. Which of the two is a USER DECISION (added to the run #4 user-decision list); not
repaired by the driver.
