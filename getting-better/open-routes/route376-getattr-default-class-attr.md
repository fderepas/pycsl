# OPEN ROUTE #376 — `getattr(o, "k", d)` FOLDS TO THE DEFAULT FOR A CLASS ATTRIBUTE OR METHOD
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r373 executor off dc378283c — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r376/`: `e47_getattr_class_attr_record.py`, `e48_getattr_inherited_attr.py`, `e96_getattr_self_class_attr_record.py`, `e98_getattr_method_record_value.py`.

Folded to the default whenever `k` is not an instance field: a class attribute (own or inherited, e47/e96/e48) or a method (e98) exists, so CPython returns it (-1 / a bound method), not the default.

Repair: Fold to the default only when no class-body binding of that name exists anywhere in the MRO (and no `__getattr__`); otherwise refuse.

## REPAIR (2026-10-25, r373 executor off dc378283c, repaired with routes #373 / #374 / #375; code 7a051eec + 9d029328, corpus e8488149 + 98378213 (5082), census 98378213, getattr sites 51f0fbb1, docs f19c7b7a + c037431b (annotations §7.36, translational §T.6.47))
**Design: a sound refusal at the ABSENT arm.** `_run_pipeline` computes from the source, per class (lower-cased as Module 6
keys records), the class-body bindings over its FILE MRO (`class_binds_r376`: `def` / `class` names, `Name` stores except a
value-less annotation, import aliases; `*` for a `__getattr__` / `__getattribute__`). In `_lower_getattr` (no mirror twin), a
`getattr(o, "k"[, d])` that route #197 classifies ABSENT (known record, `k` not a field), and route #309's
`_current_record_var_classes` arm, is REFUSED (`PYCSL-R376-GETATTR-CLASS-BINDING`) when `k` is so bound, `*` holds, the class
is not described, `k` is in `dir(object)` or is a dunder. A faithful model (the class attribute's value) was not attempted: the
per-site opaque is an `int` with every int law, wrong for a method or a `str` attribute, and the census finds no corpus /
pyref / mirror `getattr` on a known record naming a class-body binding (mirror and corpus emissions byte-identical).
**Probe table** (full proof via heavy.sh; base = dc378283c):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| e47 class attr `k = -1`, `getattr(r, "k", 0) >= 0` | 5075 | -1 | rc=0 PROVED | rc=1 REFUSED R376 |
| e48 inherited `k = -1`, `getattr(self, "k", 0)` | 5076 | -1 | rc=0 PROVED | rc=1 REFUSED |
| e96 record `self`, class attr | 5077 | -1 | rc=0 PROVED | rc=1 REFUSED |
| e98 method `k`, `v == 0` | 5078 | bound method | rc=0 PROVED | rc=1 REFUSED |
| NEW `@property k` -> -1 | 5079 | -1 | rc=0 PROVED | rc=1 REFUSED |
| NEW user `__getattr__` -> -1 | 5080 | -1 | rc=0 PROVED | rc=1 REFUSED |
| NEW `getattr(r, "__module__", 5)` | 5081 | `"__main__"` | rc=0 PROVED | rc=1 REFUSED |
| NEW ctor local `r = R()`, `getattr(r, "k", {}) == {}` (route #309 arm) | 5082 | False | rc=1 FAIL | rc=1 REFUSED |
| control: `getattr(r, "zz", 7) == 7`, no class binding of `zz` | 5093 | 7 | rc=0 PROVED | rc=0 PROVED |
Adjacent probed: `hasattr(r, "k")` for a class attribute is the opaque `hasattr_check` (not decided; unchanged).
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
**Residuals.** (1) A base class OUTSIDE the file is not read (an imported base's class attributes still let ABSENT fold to the
default) — the mirror's emitter mixins derive from imported mixins, and reading it as unknown GONE'd two mirror files (measured).
(2) UNKNOWN receivers keep route #197's per-site int opaque (int laws on a possibly non-int attribute, pre-existing).
