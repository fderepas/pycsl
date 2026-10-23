# OPEN ROUTE #319 — A LIST PARAMETER REBOUND INSIDE A NESTED BLOCK IS LOST AFTER THE BLOCK (block-scoped `let`), LATER WRITES HIT THE CALLER
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day; sound refusal), Severity 1.** Red-team round 17; driver-reproduced on main f44477b7 (rc=0; CPython violates).
Witnesses `witnesses-r319/`: `if b: xs = [7,7,7]` then `len(xs)` proves 2 (CPython 3) (p01); same in `for` (l25), element read (p03), nested if
(p08); `if b: xs = [7,7]; xs[0] = 9` proves `ensures xs[0] == 9` with `assigns xs[0]` while the CALLER's list is untouched in CPython (p14 — the
caller-visible frame is wrong). Mechanism: inside if/for/while, `xs = [...]` lowers to a block-scoped `let xs = (Array.make ...) in`; after
the block `xs` denotes the parameter again. Top-level, try and match rebinds use `ref xs` (correct or ill-typed).
Repair: a parameter (or any local) rebound anywhere in the body must be a `ref` for the whole body (or the rebind refused when it occurs
inside a nested block); writes after a rebind must target the new object, never the caller's.

## REPAIR (2026-10-23, r318 executor off 8610363c; commit 654ef3a4 + docs commit)
**Design: refusal; the `ref` model was measured ill-typed.** A hand-written `let xs = ref xs in .. xs := (Array.make ..)`
over an `array` parameter is rejected by Why3 ("This expression prohibits further usage of the variable xs") as soon as the
parameter is used afterwards (the postcondition / frame), so a whole-body `ref` is not available for array/record
parameters. **Census of first-binding paths:** scalar parameters assigned anywhere are pre-declared `let p = ref p` (faithful,
untouched); a TOP-LEVEL first binding of an array/record/dict parameter is a `let` scoping the rest of the body (faithful,
untouched: control 4121); a NESTED first binding (`if`/`for`/`while`/`with`; `try`/`match` pre-declare an ill-typed
`ref 0`, fail-closed) was the block-scoped `let` — **the hole** (lists, records 4120, dicts — the latter ill-typed after the
block). `TupleUnpack` targets use `let p = ref p` (unchanged). **Rule** (`_handle_assign_stmt`, at the first-binding test,
inline): a first binding of a formal parameter (not `self`) whose first `Assign` in source order (walk of the function's IR
body) is not at depth 0 -> `PYCSL-M6-PARAM-REBIND-NESTED-BLOCK`. Writes after a top-level rebind already target the new
object; the caller's frame is the parameter's.

| witness | CPython | 8610363c | after |
|---|---|---|---|
| 4117_gen37_r319_param_rebind_in_if (p01) | violates | PROVED | REFUSED |
| 4118_gen37_r319_param_rebind_then_store_frame (p14) | violates | PROVED | REFUSED |
| 4119_gen37_r319_param_rebind_in_for (l25) | violates | PROVED | REFUSED |
| 4120_gen37_r319_record_param_rebind_in_if | violates | PROVED | REFUSED |
| 4121_gen37_r319_param_rebind_top_level_control | ok | PROVED | PROVED |
| red-team p03 (rebind in `for k in range(1)`), p08 (nested if) | violates | PROVED | REFUSED |

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
**Residuals:** a parameter first rebound at the top level and AGAIN in a nested block takes the array-local path (route #320's
fence) or an ill-typed `:=` (fail-closed); a nested rebind whose value is dead after the block is refused (coarse).
