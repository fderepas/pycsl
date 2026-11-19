# OPEN ROUTE #476 — SCRIPT ORDER -- THE MAIN-GUARD DRIVER CALLS f BEFORE A LATER `def` REBINDS ITS CALLEE
**Status: REPAIRED (driver run #3, executor m2, 2026-10-30), Severity 1.** Red-team round 39 (2026-10-29, on d6abee90b after #463-#473: 918 probes + 1064 mode re-proofs / 141 confirmed (probe, mode) pairs; rt38's 142 counted all closed). Census TSV `scratchpad/rt39/census.tsv`; the family block below is quoted from `scratchpad/rt39/FINDINGS.txt`.
Witnesses `witnesses-r476/` (8): `g34_w103_helper_redefined_after_main.py`, `g37_v102_def_bad_f_good_after_main.py`, `g40_u900_value_redef_after_main.py`, `g40_u901_keyerror_redef_after_main.py`, `g40_u902_reversed_main_guard.py`, `g40_u903_three_defs.py`, `g40_u904_list_index_redef.py`, `g40_u905_transitive_callee_redef.py`.

Driver repro: `scratchpad/rp39/repro.sh` (session scratchpad) on d6abee90b, 2026-10-29T23:41Z: all 16 rt39 verify exemplars (2+ per family) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F3 SCRIPT ORDER -- THE MAIN-GUARD DRIVER CALLS f BEFORE A LATER `def` REBINDS ITS CALLEE (8)
  WHAT: the model resolves a name to its textually LAST def (the import view), route #459 only asks that the name be bound before the call frontier, so a callee redefined after the main guard is verified with its benign last body while the script calls the first
  EXEMPLAR: g34/w103_helper_redefined_after_main.py (`def g(x): return 1 // (x - x)`, claimed `f` returns `g(n)`, the `if __name__ == "__main__":` driver calls `f(1)`, and AFTER the guard a second `def g(x): return x`)
  CPYTHON: ZeroDivisionError when the file is run as a script: the driver calls f while g is still the FIRST def (u900: the contract `\result == n` broken, 2 for 1; u901 KeyError; u904 IndexError; u905 through a transitive callee; u902 with the reversed guard `'__main__' == __name__`; u903 three defs).
  WHY IT PROVES: The model resolves a module name to its textually LAST `def` (the IMPORT view: after a complete import, g is the second def; v100, the same file with the raising def LAST, is not proved). Route #459 (pycsl.py:15766-15790) judges only whether a name is DEFINITELY BOUND before the call frontier (the first `if __name__ == ...` statement), not WHICH binding is live there; #463 refuses re-definition only when the EARLIER binding is a claimed def; the Weaver rebinding deny-list (Module3_Weaver.py:2638) covers non-def rebindings (`g = ...`, import, for / with / except / match targets -- all refused in y105-y118) and compound-statement defs (y122, v104), not a plain top-level `def` that follows the guard. Route #469 already decided the SCRIPT entry must be judged.
  PROPOSED SYSTEMATIC REPAIR: FLOW-SENSITIVE BINDING AT THE FRONTIER: extend #459 from "bound before the frontier" to "the binding the model uses is the one live at the frontier": a name read (transitively) by a claimed function that has ANY binding after the call frontier (a second def / class / assignment textually after the `if __name__ == "__main__":` statement or a module-level call) is REFUSED, unless every binding before the frontier is identical. Equivalently (allow-list): admit a module name only when ALL its bindings precede the frontier. Witness: the 8 F3 probes; control: a def after the guard that no claimed function reads.
  PROBES: g34/w103_helper_redefined_after_main.py g37/v102_def_bad_f_good_after_main.py g40/u900_value_redef_after_main.py g40/u901_keyerror_redef_after_main.py g40/u902_reversed_main_guard.py g40/u903_three_defs.py g40/u904_list_index_redef.py g40/u905_transitive_callee_redef.py
```

## Repair (driver run #3, m2)

THE BINDING LIVE AT THE CALL FRONTIER (the proposal's first form, without the "identical bindings"
exemption), in `_run_pipeline` (`src/pycsl/pycsl.py`, block `ROUTE #476`, beside #459; the mirror
twin is `\trusted`): when the module has a call frontier (the first top-level `if` testing
`__name__` -- either operand order -- or statement holding a module-level call of a verified
function or of a file def / class that transitively calls one; route #459's definition), a module
name read by a VERIFIED function (every non-`\trusted`, non-`\abstract` function, whatever its
contract -- not only `no_exception` claims) -- directly or through the bodies of EVERY top-level
def / class binding that name, transitively -- or the verified function's own name, which is bound
both by a top-level statement BEFORE the frontier and by the frontier statement or one AFTER it, is
REFUSED (`PYCSL-R476-REBOUND-AFTER-FRONTIER`). Two bindings both before the frontier stay admitted
(the last one is live at the frontier and is the model's). A `from m import *` stops the judgement
(#459). Witnesses: all 8 in `witnesses-r476/` REFUSED; driver probes: a module-level call frontier
(no main guard; already refused at base by the import-time-call rule), a constant `K` rebound after
the guard (not proved at base), REFUSED. Corpus witnesses `7540`-`7545`; controls `7547` (a def after
the guard no verified function reads) and `7548` (two defs of `g` before the guard) PROVE, as does
rt39's PASS control `g37/v101_def_bad_then_good`. Over-refusal: pure-`ast` census of the rule over
the corpus (6952 files) and mirror + stdlib (157): 0 files. The broader allow-list (refuse a read
name with ANY binding at / after the frontier) would hit 19 corpus files (other routes' witnesses
of a global bound after `__main__`, already route #459's NameError territory) and was not taken;
route #459's transitive NameError (`f -> k -> g`, `g` only after the guard) was probed and is
already refused at base (#459 + #460's reached claim).
