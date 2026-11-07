# OPEN ROUTE #499 — A CONSTANT `exec("...")` INSIDE A FUNCTION IS SPLICED AS IF ITS ASSIGNMENTS REBOUND THE FUNCTION's LOCALS: CPYTHON (PEP 667) RUNS IT AGAINST A SNAPSHOT OF locals(), SO `x = 1; exec("x = 2"); return x` RETURNS 1
**Status: REPAIRED (executor u4, driver run #4, 2026-11-01, off 5a9e2e161; see REPAIR below), Severity 1.** Red-team round 44 (driver run #4, 2026-11-01, on 1c30f94b3 = main: 793 probes in g500-g527, 779 CPython-breaching, 139 confirmed (probe, mode) pairs on 111 probes in 5 families). Census `scratchpad/rt44/census.tsv`; the family block below is quoted from `scratchpad/rt44/FINDINGS.txt`.
Witnesses `witnesses-r499/` (11): `g507_s50719_exec_local.py`, `g517_e51700_assign_local.py`, `g517_e51701_assign_param.py`, `g517_e51702_augassign_local.py`, `g517_e51705_assign_from_param.py`, `g517_e51706_two_stmts.py`, `g517_e51707_multiline.py`, `g517_e51708_list_rebind.py`, `g517_e51709_str_local.py`, `g517_e51710_guard_then_div.py`, `g517_e51717_tuple_assign.py`.

Driver repro: session scratchpad `rp44/repro.sh` on 1217d2745 (main's code), 2026-11-01T02:20Z: all 12 rt44 verify exemplars rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F4 A CONSTANT `exec("...")` INSIDE A FUNCTION IS SPLICED AS IF ITS ASSIGNMENTS REBOUND THE FUNCTION's LOCALS: CPYTHON (PEP 667) RUNS IT AGAINST A SNAPSHOT OF locals(), SO `x = 1; exec("x = 2"); return x` RETURNS 1 (11)
  EXEMPLAR: g517/e51700_assign_local.py: `#@ ensures \result == 2` f(n): `x = 1; exec("x = 2"); return x`
  CPYTHON: f(0) -> 1 (VIOLATION contract 1); e51710 (`d = 0; exec("d = 5"); return 10 // d` under no_exception \all) -> ZeroDivisionError
  PYCSL CMD: cd /home/fabrice/git/pycsl-rt44 && PYTHONHASHSEED=0 PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py /home/fabrice/git/pycsl/scratchpad/rt44/g517/e51700_assign_local.py --import-path src/pycsl   (CPython: cd /home/fabrice/git/pycsl/scratchpad/rt44/g517 && /home/fabrice/git/pycsl-rt44/.venv/bin/python3 -E -s e51700_assign_local.py)
  WHY: src/pycsl/frontend/exec_splice.py (`_ExecSplicer.visit_Expr`) replaces every constant exec expression-statement by its parsed body regardless of scope; the inline-equivalence it asserts holds only at module (and class-body) scope. REPAIR: splice only outside function bodies, or refuse a Name / AnnAssign / AugAssign / unpacking target inside a function.
  PROBES: g507/s50719_exec_local.py g517/e51700_assign_local.py g517/e51701_assign_param.py g517/e51702_augassign_local.py g517/e51705_assign_from_param.py g517/e51706_two_stmts.py g517/e51707_multiline.py g517/e51708_list_rebind.py g517/e51709_str_local.py g517/e51710_guard_then_div.py g517/e51717_tuple_assign.py
```

## REPAIR (executor u4, driver run #4, 2026-11-01; annotations §7.499)

Inline in `pycsl.py::_run_pipeline` on the woven AST just before `splice_constant_exec` (mirror twin `\trusted`; the
splicer itself untouched; no new def, no axiom), new code `PYCSL-R499-EXEC-IN-FUNCTION-SCOPE`, refuse by default: in a
function scope, a constant exec whose text parses and passes the splice whitelist is admitted only when every name it binds
(name / tuple / starred target of an assignment, augmented, annotated, walrus) is named NOWHERE else in the function (the
snapshot binding is unobservable) and the function reads no namespace (`locals` / `vars` / `dir` / `globals` / `eval` /
another `exec`), and the text has no lambda / comprehension / `yield` / `await`; a constant exec in a class body nested in a
function is refused (class-body exec cannot read the function's names); a constant exec with `globals=` / `locals=` by
keyword is refused at every scope (the splicer reads only the positional text). Element / attribute stores and calls stay
spliced; a text the whitelist rejects keeps the splicer's own refusal (0643 / 1756 / 1757 / 1802 unchanged).
Corpus `0642` (`exec("x = 5\ny = x + 1"); return y` in a function, claimed 6) was this false proof (CPython NameError):
flipped to expected FAIL.


Witnesses: all 11 in `witnesses-r499/` REFUSED (`PYCSL-R499-EXEC-IN-FUNCTION-SCOPE`) under default / typed / store (33/33
runs). Corpus 7920-7924 / 7926 / 7927 (PROVED at base, REFUSED), 7925 (typed: Why3 type error at base, refused by name);
`0642` flipped to expected FAIL; controls 7930 (`exec("xs[0] = 5")` in a function), 7931 (module-level exec), 7932 (a binding
the function never names: rt44 control e51704) PROVED. Advice followed: the statement inline (a499_write_inline) and the
exec at module level (a499_exec_at_module_level) VERIFY. Over-refusal: corpus root GONE only 0642 (the false PASS);
pyref / mirror byte-inert; rt43 / rt44 controls: none newly refused. Cost: an honest exec in a class body nested in a function
is refused. Commit: 7cc96344e.
