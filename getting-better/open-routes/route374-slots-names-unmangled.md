# OPEN ROUTE #374 — `__slots__` NAMES ARE COMPARED UNMANGLED
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r373 executor off dc378283c — sound refusal after mangling, see REPAIR). Was OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r374/`: `s05_slots_mangled_subclass.py`, `s21_slots_mangled_external.py`, `s22_slots_mangled_own_class_ok_read.py`, `s27_slots_mangled_external_read.py`, `s29_slots_dc_slots_mangled.py`.

Slot names and store names are compared as written: `self.__x` in a subclass (`_B__x`) and `a.__x` outside the class pass #360 (CPython AttributeError: no `__dict__`); conversely s28 over-refuses the real slot `self._A__x`.

Repair: Mangle both sides (per defining class) before comparing.

## REPAIR (2026-10-25, r373 executor off dc378283c, repaired with routes #373 / #375 / #376; code ada49f2d, corpus e8488149 + 0c64cab1, census 98378213, docs f19c7b7a (annotations §7.36, translational §T.6.47))
**Design: mangle both sides (CPython's `_Py_Mangle`), no emission change.** In the #360 store check of `_run_pipeline` (mirror
twin `\trusted`, inline): each `__slots__` entry `__x` (two leading underscores, not a dunder) is mangled by the class that
DECLARES it (`_` + class name without leading underscores + `__x`; `@dataclass(slots=True)` fields too), and an attribute store
spelling `o.__x` by its innermost lexically enclosing `ClassDef` (one pre-walk, `_mg374`; module scope: no mangling; a
`setattr` / `delattr` string is never mangled). The comparison and the refusal message use the mangled names.
**Probe table** (full proof via heavy.sh; base = dc378283c):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| s05 slot `__x` in A, `self.__x` in B(A) (`_B__x`) | 5058 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| s21 external `a.__x = 2` (`__x` vs `_A__x`) | 5059 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| s22 B(A) slots `y`, stores `self.__x` | 5060 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| s27 external `a.__x = 5` | 5061 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| s29 B(A) stores `self.__v` | 5062 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| s23 literal slot `_A__x`, B stores `self.__x` | 5063 | AttributeError | rc=1 REFUSED | rc=1 REFUSED |
| s24 dunder slot `__x__` (unmangled) + `self.__y` | 5064 | AttributeError | rc=1 REFUSED | rc=1 REFUSED |
| s28 class `_A`, B stores `self._A__x` and `self.__x` | 5065 | AttributeError (`_B__x`) | rc=1 REFUSED (on the real slot) | rc=1 REFUSED (on `self.__x` only) |
| control: `self.__x` in A, `self._A__x` and `self.__z` in B(A) | 5091 | ok | rc=1 REFUSED (over-refusal) | rc=0 PROVED |
**Blast radius** (base worktree at dc378283c vs candidate 9d029328, `bin/byte-diff-sweep.sh` + `bin/byte-diff-compare.py`,
shared by routes #373-#376): root 2341 base / 2357 candidate, **0 MOVED / 0 GONE / 0 APPEARED** (17 of the 37 new sources
emit, the rest refuse; one GONE in the first compare, `1723_route212_verify_imports_control`, is a resource artefact —
`--verify-imports` proves its dependency inside the emission and timed out under load; it failed the same way at BASE when
re-run standalone, and re-emitted individually via heavy.sh it is byte-IDENTICAL to the base emission); pyref 2186/2186
0/0/0; mirror 53/53 0/0/0 (`bin/mirror-emit-sweep.sh`, `--min-files 50`) — **no mirror mover, no OWED whole-file proof**.
MEASURED on the way (first candidate, then narrowed): the mirror GONE'd `errors.py` (a bare `__str__` call spelling matched a
method's short name: the #373 rule is now keyed on the SOURCE's nested-in-a-method def names), `module6_whyml/expressions` and
`statements` (`getattr(self, "_x", d)` on emitter mixins deriving from IMPORTED mixins: the "outside base = unknown" arm of #376
was dropped, a recorded residual), and MOVED `frontend/pure_ast` (`self.set_precedence(p, *node.comparators)`: a starred CALL
argument is asserted under `no_exception` only). Ledger 3, no new def, one new refusal code
(`PYCSL-R376-GETATTR-CLASS-BINDING`, 2 raise sites, both witnessed), no gate loosened.
**Gates** (one run for routes #373-#376 on the final tree; logs in the executor scratchpad `r373/g/`): witnesses / controls
above (full proof via heavy.sh, base dc378283c vs candidate); byte-diff root + pyref and mirror sweep (above, rc=0 after the
1723 re-emission); `check-self-annotate-sync.sh` rc=0 (926 verbatim); `self-annotate-mirror-check.sh` rc=0 (53);
`check-trusted-reasons` rc=0 (420 / 420, unclassified 259); `check-trusted-raises-honesty` rc=0 (19 / 61, ratchet 61 — the
R376 raises sit in `_lower_getattr`, which has no mirror twin; #373 / #375 add no raise); `check-assigns-underdeclaration
--transitive` rc=0; `check-dropped-mutation` rc=0 (0 / 51 / 5 / 0); `check-refusal-witness-coverage` rc=0 (303 demonstrated,
5 not = ceiling 5; rows 5050-5082 via `_census_row`); `doc-coherency --check` rc=0; `check-getattr-erasure` rc=0 (DECLARED 0; rows for 5082 (UNKNOWN 1, refused after the census line) and control 5093 (ABSENT 1) registered by `--emit-baseline`, diff = exactly those two rows);
`check-assumed-facts` rc=0 (85 facts, ledger 3); `run-soundness-planes.sh` fast 61/61 rc=0 (`--slow` not run); `check-stdlib-modules-verify` rc=0 (one command via heavy.sh: 104 modules, 83 VERIFY, the known 21).
**Residuals.** (1) As route #360: receivers of unknown class, imported bases, `__slots__` under control flow are not checked.
(2) Mangling is applied to the slots check only; the record model's field names (`self.__x` read in A, `b.__x` outside) are
still the unmangled spellings (a read through a different spelling is a missing-field read, fail-closed or opaque).
