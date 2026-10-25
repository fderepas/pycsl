# OPEN ROUTE #363 — `super(X, self).__init__()` IS CREDITED TO THE DIRECT BASE WHATEVER X IS
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r360 executor off fcc2c822 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r363/`: `r35_super_skip_class.py`, `r42_super_skip_reads_m.py`.

Route #347's constructor-chain summary credits the direct base's `__init__` regardless of X: `super(A, self)` really runs `object.__init__` (r35), `super(M, self)` really runs `A.__init__` (r42); a field read under no_exception proves; CPython AttributeError. (Over-refusal r41 shows the converse.)

Repair: Resolve `super(X, self)` to the class after X in the linearised MRO; refuse when X is not a file class.

## REPAIR (2026-10-25, r360 executor off fcc2c822; code 6550de83, corpus eae6a9d8 + dea007f9, census 69d1e9f2, docs 5be7bed4 + route docs)
**Design: sound refusals plus a sharper #347 summary, no emission change** — inline additions to the #346-#349 block of
`_run_pipeline` (mirror twin `\trusted`; no new def; ledger 3), shared by routes #360-#363 (annotations §7.32, translational
§T.6.43). New shared facts: each `@dataclass`'s InitVar / KW_ONLY pseudo-fields, each class's literal `__slots__`, and each
class's C3 MRO over the file's classes (an outside base is a leaf).
**Why this repair.** The constructor itself is already handled soundly elsewhere: Module 5 models only an argument-less leading
`super().__init__(..)`, so `super(X, self)` leaves the construction opaque (route #150), route #335's chain ends at it, and on an
invariant class route #342 refuses it (`self` escapes as an argument: measured on `q363inv` / `q363inv2`, REFUSED R342 at base and
after). Only #347's definite-assignment summary credited the wrong constructor. RULE (#347 summary): `super().__init__(..)` keeps
crediting the first ancestor's set; `super(X, s).__init__(..)` with `X` a class name, `s` the constructor's own first parameter, a
successful C3 linearisation of the class and `X` on it, credits the set of the first class AFTER `X` in that MRO (nothing past a
non-file class: `object.__init__` stores nothing); any other shape (X not a file class, not on the MRO, a failed C3, other
arguments) credits NOTHING — the sound direction, so a dependent read is refused by `PYCSL-R347-FIELD-MAYBE-UNASSIGNED`.
**Probe table** (full pycsl proof via heavy.sh; base = fcc2c822):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| r35 `super(A, self)` in `B(A)`, read `b.x` | 4868 | AttributeError | rc=0 PROVED | rc=1 REFUSED R347 |
| r42 `super(M, self)` in `B(M(A))`, read `b.m` | 4869 | AttributeError | rc=0 PROVED | rc=1 REFUSED R347 |
| control: `super(M, self)`, reads A's `x` and B's `n` (the r41 over-refusal shape) | 4885 | 1 | rc=0 | rc=0 PROVED |
| control: `super(B, self)` (two-argument `super()`) | 4886 | 1 | rc=0 | rc=0 PROVED |
Scratch, not filed: `super(M, self).v()` / `super(A, self).v()` in a METHOD FAIL at base and after (opaque call); a diamond
`D(B, C)` whose `B.__init__`'s `super()` really runs `C.__init__` (`q363dia`) is REFUSED at base and after (by-name union of #347).
**Census / blast radius.** `__slots__`: 8 files in the corpora / mirrors / `pycsl_lib` (pyref 0079, corpus 0900 / 0901 / 0975,
mirrors Module1_Ingestor / Module2_Parser / pure_ast, `pycsl_lib/re/_engine.py`), none storing outside its slots; InitVar: 1 user
(corpus 4058, never read as an attribute; REFUSED at base by route #315, unchanged), KW_ONLY: 0, `super(X, self)`: 0; no
invariant-carrying dataclass with a pseudo-field. Root / pyref / mirror byte-diffs 0 MOVED / 0 GONE / 0 APPEARED and the 4
`pycsl_lib` files with slots / dataclasses / `super(` give byte-identical `--no-proof` output base vs candidate: nothing newly refused.
**Gates** (logs in the executor scratchpad `r360/g/`; rc): witnesses / controls above (full proof via heavy.sh, base fcc2c822 vs
candidate); byte-diff-compare root rc=0 (2313 base / 2320 candidate: 0 MOVED / 0 GONE / 0 APPEARED, 7 new control sources), pyref
rc=0 (2186/2186 0/0/0, `--min-files 2000`), mirror rc=0 (53/53 0/0/0, `--min-files 50`: **no OWED proof**);
check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); check-getattr-erasure rc=0;
check-stdlib-modules-verify rc=0 (one command via heavy.sh: 104 modules, 83 VERIFY, the known 21 non-verifying); run-soundness-planes.sh fast **61/61** rc=0; `--slow` NOT run; doc-coherency --check rc=0;
check-assumed-facts rc=0 (85 facts, all reviewed families); check-dropped-mutation rc=0 (0 / 51 / 5 / 0); check-refusal-witness-coverage
rc=0 (300 demonstrated / 5 not, ceiling 5; rows 4850-4869 via `_census_row`); check-trusted-reasons rc=0 (420 / 420);
check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3, HOLE 0);
check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) The summary resolves `super` against the DEFINING class's MRO, not the instance's (cooperative `super()` in
a diamond): measured masked by #347's by-name union (`q363dia` REFUSED), not proven impossible in general. (2) An imported base's
constructor is not analysed (per-file, as #347 residual (4)).
