# OPEN ROUTE #386 — A DEF NESTED IN A METHOD NAMED LIKE A BUILTIN STILL LOWERS TO THE BUILTIN
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r386 executor off 5addbdeef — sound refusal, see REPAIR; shared with #387). Was OPEN, Severity 1.** Red-team round 30 (2026-10-25, probes around #373-#380 and route #226 increment 2c); driver-reproduced on main a064a298f (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt30/driver-repro.txt`).
Witnesses `witnesses-r386/`: `d03_nested_def_shadows_builtin_len.py`, `d13_nested_def_shadows_max_in_method.py`, `d21_nested_def_shadows_min_in_method.py`.

`def len(..)` / `max` / `min` nested in a method: the bare call lowers to the builtin model (e.g. `MinMax.max`); #373's rule fires only for unresolved calls. CPython 0 / -100 / 100 against the ensures.

Repair: A bare call whose name is bound locally in the enclosing scope (nested def, import, loop / with / except target) never resolves to a builtin or library model.

## REPAIR (2026-10-25, r386 executor off 5addbdeef, repaired with route #387; code 13fbfa1ed + a1b4a8dd6, corpus ebed9c6e7, docs 475527100 (annotations §7.41 / translational §T.6.52), census d3fffd4f9, route docs)
**Design (shared by #386 / #387): sound refusals in Module 3 `Module3_Weaver.process` (mirror twin `\trusted`), no emission change,
no new def, no new raise site, ledger 3.** Route #131's arm ("a builtin name bound by a store in a scope where it is also read",
raise "a name's runtime value is not the one the model reads") already refused stores, loop / with / except targets and
parameters named like a builtin. RULE (#386): the same refusal now also fires when the builtin name is bound in a function /
method body by a nested `def` / `class`, or in the module or a function body by an `import` / `from .. import` other than one from
`builtins` / `__builtin__`, and is read anywhere under that scope (nested scopes included); and when a LAMBDA parameter or a
COMPREHENSION target is named like a builtin and read under that node. A module-level user `def len` keeps route #75's model; a
method named like a builtin (class scope) is unchanged. The erasure of route #373 was not needed: refusing measured inert.
**Probe table** (full pycsl proof via heavy.sh; base = 5addbdeef worktree; corpus copies 5290-5299 / 5320-5324):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| d03 nested `def len` in a method | 5290 | 0 | rc=0 PROVED | rc=1 REFUSED (route #386) |
| d13 nested `def max` in a method | 5291 | -100 | rc=0 PROVED | rc=1 REFUSED |
| d21 nested `def min` in a method | 5292 | 100 | rc=0 PROVED | rc=1 REFUSED |
| q01 nested `def max` in a plain function | 5293 | -100 | rc=1 FAIL (unknown) | rc=1 REFUSED |
| NEW latent q02 `lambda max: max(1, 2)` | 5294 | 1 | rc=0 PROVED | rc=1 REFUSED |
| q03 comprehension target `max` | 5295 | 1 | rc=1 FAIL (WhyML type error) | rc=1 REFUSED |
| NEW latent q04 local `from operator import sub as max` | 5296 | 2 | rc=0 PROVED | rc=1 REFUSED |
| q05 nested `def len` read in a closure | 5297 | 0 | rc=1 FAIL (timeout) | rc=1 REFUSED |
| q06 local `class abs` | 5298 | 0 | rc=1 FAIL | rc=1 REFUSED |
| NEW latent q09 module-level `from operator import sub as max` | 5299 | 2 | rc=0 PROVED | rc=1 REFUSED |
| control: nested `helper` beside builtin `max` | 5320 | 3 | rc=0 PROVED | rc=0 PROVED |
| control: method named `max`, `self.max()` | 5321 | 7 | rc=0 PROVED | rc=0 PROVED |
| control: local `from builtins import max` | 5324 | 3 | rc=0 PROVED | rc=0 PROVED |
**Census / blast radius.** Before landing (both corpora, 53 mirrors, `pycsl_lib`, live `src/pycsl` as a mirror dependency):
#386 — a def / class nested in a function and named like a builtin AND read: 1 (3784's local `class KeyError`, expected FAIL,
already refused by route #305); imports binding a builtin name: `pycsl_lib/re` (`from ._engine import compile`, never read —
admitted), 1374 / 3789 (`from builtins import ..`, route #131's own arm); lambda parameters / comprehension targets named like a
builtin and read: 0; method-level `def next` (pure_ast) and module-level user `def len` / `ord` / `min` (route #75's 1182-1187)
are class / module scope and unchanged. #387 — class-body `global` / `nonlocal`: 0; members under a class-body compound
statement: 1355 (route #122, refused), 4821 (refused by PYCSL-SEM-OVERRIDE-REFINEMENT), and control 4940 (`__eq__` under
`if True:`) — the FIRST candidate sweep GONE'd 4940, so the body of a literal `if True:` is admitted (20ccfe42d); no
`if TYPE_CHECKING:` member. Final sweeps (code 20ccfe42d): root 2405 base / 2411 candidate .mlw, **0 MOVED / 0 GONE / 0 APPEARED**
(6 new control sources emit, 21 new witnesses refuse); pyref 2186 / 2186 0/0/0 (`--min-files 2000`); mirror 53 / 53 0/0/0
(`--min-files 50`) — **no mirror mover, no OWED whole-file proof**.
**Gates** (rc, one run for routes #386 / #387 on the final tree; logs in the executor scratchpad `r386/g/`): witnesses / controls
above (full proof via heavy.sh, base 5addbdeef worktree vs candidate); byte-diff-compare root rc=0, pyref rc=0, mirror rc=0
(above); check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast
**61/61** rc=0 (`--slow` NOT run); check-getattr-erasure rc=0 (DECLARED 0; ABSENT 10 / UNKNOWN 43 unchanged); check-stdlib-modules-verify rc=0 (83 VERIFY, the known 21 non-verifying) (one command via heavy.sh);
doc-coherency --check rc=0; check-assumed-facts rc=0 (85 facts, all reviewed families; ledger 3); check-dropped-mutation rc=0 (0 / 51 / 5 / 0);
check-refusal-witness-coverage rc=0 (310 demonstrated / 5 undemonstrated = ceiling 5; no new raise site; rows 5290-5310 via
`_census_row`); check-trusted-reasons rc=0 (420 / 420, ratchet 259); check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61);
check-assigns-underdeclaration --transitive rc=0 (TRAP 3, HOLE 0).
**Residuals.** (1) A refusal, not a model: a nested def / local import named like a builtin is never lowered (route #373's
erasure could admit some, unmeasured demand: 0 census users). (2) Shadowing through `globals()["len"] = ..`, `builtins.len = ..`
or a star import is not covered here (routes #118 / #130 / #131 own those). (3) A function-local import of a name that is not a
builtin but equals a module-level import is route #130's arm, unchanged.
