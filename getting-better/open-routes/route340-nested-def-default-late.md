# OPEN ROUTE #340 — A NESTED def's DEFAULT ARGUMENT THAT IS A BARE NAME IS EVALUATED AT CALL TIME (Python: at def time)
**Status: REPAIRED, candidate (gen #37, 2026-10-24; opened the same day), Severity 1.** Red-team round 24; driver-reproduced on main (rc=0; CPython violates).
Witnesses `witnesses-r340/`: the lifted `g(y)` is called as `(g !x)` after `x` was rebound (c04; c12 outer parameter; c20 `x += 1`; c36 ZeroDivisionError under
no_exception). Route #273's check accepts a Name default as "literal".
Repair: a nested def's default expressions are evaluated ONCE at def execution: bind them to fresh immutable names at the def site (in
Python order) and use those at calls, or refuse any non-literal (incl. bare-name) default of a nested def.

## REPAIR (2026-10-24, r339 executor off 5e517ffc; code d336bd01, corpus adea2535, docs 0b3e2c03, census 9b14185e)
**Design: refuse, not re-evaluate.** Inside route #273's definition-time block (`_run_pipeline`, mirror twin `\trusted`;
no new def; no emission change; ledger 3), the bare-`Name` case of the "literal default" predicate is narrowed. CENSUS
before landing (CPython `ast` prototype over pycsl-reference, python-reference, the self-annotate mirror, `pycsl_lib`):
every bare-name default of a nested def / lambda is either 2967's NEVER-REBOUND parameter `x` (admitted) or sits inside
a default already refused as non-literal (2960 `10 // x`, 2963 `push(xs)`, `json/encoder.py::iterencode`). A def-site
binding (`let _d_g_y = !x in` at the def, used at every call) would move the lifting machinery for zero users; the
refusal moves nothing. Annotations §7.26 (2), translational §T.6.37 (+ a sentence in the #273 paragraph).
RULE (`PYCSL-SEM-DEF-TIME-EVALUATION`, new message "bare-name default ... REBOUND"): a bare-name default (also inside a
tuple/list/set/dict display) of a nested `def` / `async def` / `lambda` of a lowered function `F` is admitted only if the
name is bound nowhere in `F` (store/del `Name`, nested `def`/`class` name, import alias, `except`/`match` capture, in any
nested scope) and is declared `global`/`nonlocal` nowhere in the module. Then its def-time value equals the call-time
read `(g !x)`. Lambdas are covered by the same predicate (the lambda probes `g = lambda y=x: y; x = 2; g()` and `lambda y=i: 1 // y`
under `no_exception` were already refused at base for other reasons: an erased lambda result / an unverified callee).

**Probe table** (full pycsl proof via heavy.sh; base = 5e517ffc worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| c04 `x = 1; def g(y=x); x = 2; g()`, `\result == 2` | 4602 | violates (1) | rc=0 PROVED | rc=1 REFUSED |
| c12 parameter rebound `x = x + 1` | 4603 | violates | rc=0 PROVED | rc=1 REFUSED |
| c20 `x += 1` | 4604 | violates | rc=0 PROVED | rc=1 REFUSED |
| c36 `i = 0; def g(y=i)` (`1 // y`), `i = 5`, `no_exception \all` | 4605 | ZeroDivisionError | rc=0 PROVED | rc=1 REFUSED |
| control: never-rebound parameter + module constant defaults | 4606 | ok | rc=0 | rc=0 PROVED |
| (2967, route #273 control: `z: int = x` parameter) | 2967 | ok | emitted | byte-identical |
**Blast radius** (shared run with route #339): root 0 MOVED / 0 GONE / 0 APPEARED; pyref 2186/2186 0/0/0; mirror 53/53
0/0/0 — no OWED proof, no latent false proof beyond the witnesses.
**Gates** (routes #339 + #340, one run, all rc=0): witnesses 14/14 PROVED -> REFUSED, controls 3/3 PROVED; byte-diff root /
pyref / mirror above; fidelity `check-self-annotate-sync.sh` (926 verbatim) + `self-annotate-mirror-check.sh` (53/53);
`run-soundness-planes.sh` fast 61/61 green; check-stdlib-modules-verify rc=0 (83 VERIFY, known 21 non-verifying); doc-coherency --check OK;
check-assumed-facts OK; check-trusted-raises-honesty OK (ratchet 61); check-refusal-witness-coverage OK (287
demonstrated, 5 undemonstrated = ceiling; rows via `_census_row`); check-dropped-mutation OK (0/51/5/0).
**Residuals.** (1) Over-refusal: a local bound ONCE before the def and never rebound (`x = 1; def g(y=x)`) is refused
(0 users). (2) A module-level name rebound by module code AFTER a function is defined but before it is called (only in
unverified import-time code) is outside the check, as is a module global rebound through `globals()[...]` / `exec`.
(3) Module-level def defaults stay outside (#273 residual).
