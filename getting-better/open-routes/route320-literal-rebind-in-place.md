# OPEN ROUTE #320 — REBINDING A LOCAL LIST TO A LIST LITERAL OVERWRITES THE SAME ARRAY IN PLACE (aliases see the new contents)
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day; sound refusal), Severity 1.** Red-team round 17; driver-reproduced on main f44477b7 (rc=0; CPython violates).
Witnesses `witnesses-r320/`: `ys = xs; xs = [7, 8]; return ys[0]` proves 7 (CPython 1) (p10); same with the rebind inside an if (p17);
`for x in xs: t += x; xs = [100]*4-literal` — the loop reads the overwritten elements, `\result != 10` proves (CPython 10) (l49).
Mechanism: `xs = [7, 8]` on an existing local list emits `xs_len := 0; xs[!xs_len] <- 7; ...` into the existing `Array.make` instead of a
fresh array. #279 refuses only a MUTATED alias; a non-literal RHS is refused; the literal path is the hole.
Repair: a literal rebind of a local list must allocate a fresh array (ref rebinding) or be refused when the local may be aliased
(any prior `ys = xs`, iteration in progress, passed to a callee, stored in a container/field).

## REPAIR (2026-10-23, r318 executor off 8610363c; commit 654ef3a4 + docs commit)
**Design: refusal on any possible holder.** A fresh-array rebinding would need the array local promoted to a `ref (array
int)` (the representation is `let xs = Array.make ..` + `xs_len`, not rebindable; #18 already refuses non-literal
rebinds for the same reason), touching every array-local reader; the refusal moved no corpus file. **Rule**
(`_handle_assign_stmt`, before `_emit_array_local_reassign`'s literal arm; inline flow-insensitive walk of the function's
IR body, specs skipped): REFUSED (`PYCSL-M6-LIST-LITERAL-REBIND-ALIASED`) when the local occurs as a `Var` anywhere other
than a subscript/slice base, an element/slice store or `del` target, an argument of `len sum min max sorted any all list
tuple set str repr print bool`, a comparison operand, a `test` (truthiness, corpus 1804/1822), `not`, a plain `return`,
or a `for` iterable; or it is bound from anything but a list literal/comprehension (`ys = xs; ys = [7, 8]`), a tuple
unpack or a `for` target; or the rebind lies inside a `for` whose iterable mentions it. Reuses the #279/#303 whole-body walk
pattern; #279/#81/#59 untouched.

| witness | CPython | 8610363c | after |
|---|---|---|---|
| 4122_gen37_r320_literal_rebind_through_alias (p10) | violates | PROVED | REFUSED |
| 4123_gen37_r320_literal_rebind_during_iteration (l49) | violates | PROVED | REFUSED |
| 4124_gen37_r320_literal_rebind_in_if_through_alias (p17) | violates | PROVED | REFUSED |
| 4125_gen37_r320_literal_rebind_of_the_alias | violates | FAIL | REFUSED |
| 4126_gen37_r320_literal_rebind_unaliased_control | ok | PROVED | PROVED |
| 4127_gen37_r320_rebind_after_loop_control | ok | PROVED | PROVED |

**Gates** (worktree off 8610363c): corpus byte-diff root 1 MOVED (`0708`, #318 capture of `!m`, PASS -> PASS re-proved
rc=0) and 3 GONE (`3578`/`3580`/`3582`, route #300 expected-FAIL witnesses whose list/dict parameter is rebound in an `if` arm:
FAIL -> REFUSED by #319); pyref 0 MOVED / 0 GONE (2186/2186); mirror-emit-sweep (`--min-files 50`) 1 MOVED
(`frontend/Module3_Weaver` `_desugar_for`: `let _stop_idx_m = !hi in` — `hi` is not written in the loop), L3-tc rc=0;
fidelity `check-self-annotate-sync.sh` rc=0 (926 verbatim), `self-annotate-mirror-check.sh` rc=0 (53); `doc-coherency --check`
rc=0; `check-assumed-facts` rc=0 (85 facts, unchanged); raises-honesty rc=0 (ratchet 61 silent, unchanged: both new raises sit
in `_handle_assign_stmt`, whose `\trusted` twin already declares `#@ raises PyCSLSemanticError`); `check-dropped-mutation`
rc=0 (0/51/5/0); `check-refusal-witness-coverage` (no flags) rc=0 (261 demonstrated, 5 undemonstrated = base; census rows for
4110-4114/4117-4120/4122-4125 produced by `_census_row`); `run-soundness-planes.sh` (fast) rc=0, 61/61. Moved mirror function `pycslweaver___desugar_for` re-proved
(`--fun`, rc=0); the whole-file `src/self-annotate/src/frontend/Module3_Weaver.py` proof is OWED (`HEAVY_LOW=1 heavy.sh
.venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/Module3_Weaver.py --import-path src/pycsl`). Ledger 3; no gate
loosened; no new def / field / IR change (lesson a4: inline walks).
**Residuals:** coarse — passing the list to any user callee before a literal rebind refuses even when the callee keeps no
reference; a lambda/closure capture is refused only via the value-position test.
