# OPEN ROUTE #361 — DATACLASS `InitVar` / `KW_ONLY` PSEUDO-FIELDS ARE COUNTED AS STORED FIELDS
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r360 executor off fcc2c822 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r361/`: `r23_initvar_read_k.py`, `r26_kw_only_sentinel_read.py`, `r29_initvar_arith_ensures.py`.

`k: InitVar[int]` and `_: KW_ONLY` join the synthesized field set (ClassVar is correctly excluded), so route #347's definite-assignment check credits them: reading `d.k` / `d._` under no_exception proves (r29 even proves `\result == 5`); CPython AttributeError.

Repair: Exclude `InitVar[...]` and `KW_ONLY` (string and `dataclasses.` spellings) from the dataclass field set and record type, like ClassVar.

## REPAIR (2026-10-25, r360 executor off fcc2c822; code 6550de83, corpus eae6a9d8 + dea007f9, census 69d1e9f2, docs 5be7bed4 + route docs)
**Design: sound refusals plus a sharper #347 summary, no emission change** — inline additions to the #346-#349 block of
`_run_pipeline` (mirror twin `\trusted`; no new def; ledger 3), shared by routes #360-#363 (annotations §7.32, translational
§T.6.43). New shared facts: each `@dataclass`'s InitVar / KW_ONLY pseudo-fields, each class's literal `__slots__`, and each
class's C3 MRO over the file's classes (an outside base is a leaf).
**Why a refusal.** Removing the pseudo-fields from the record type is an emission change in Module 5 (a mirrored file) and the
read would still need a value: CPython raises (no default) or reads the CLASS default (`k: InitVar[int] = 7` gives `D(1, 5).k ==
7`). Refusing the access is local and inert (0 users). RULE `PYCSL-R361-DATACLASS-PSEUDO-FIELD`: a pseudo-field is a `@dataclass`
class-body annotation whose head (through a string annotation and one subscript) is `InitVar` or `KW_ONLY` (bare or
`dataclasses.`-dotted); pseudo-fields leave #347's definite-assignment and field sets (as `ClassVar`); an attribute access (load,
store, `del`; `getattr` / `setattr` / `delattr` by literal name) of a pseudo-field NAME (any receiver but an imported module) in a
function that is not `\trusted` / `\abstract` is REFUSED — under any contract, not only `no_exception` (r29 has none).
**Probe table** (full pycsl proof via heavy.sh; base = fcc2c822):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| r23 `d.k` under `no_exception \all` | 4860 | AttributeError | rc=0 PROVED | rc=1 REFUSED R361 |
| r26 `d._` (KW_ONLY sentinel) | 4861 | AttributeError | rc=0 PROVED | rc=1 REFUSED R361 |
| r29 `D(1, 5).k == 5` | 4862 | AttributeError | rc=0 PROVED | rc=1 REFUSED R361 |
| (new) defaulted `k: InitVar[int] = 7`, `D(1, 5).k == 5` | 4863 | 7 | rc=0 PROVED | rc=1 REFUSED R361 |
| (new) string `"dataclasses.InitVar[int]"` | 4864 | AttributeError | rc=0 PROVED | rc=1 REFUSED R361 |
| control: InitVar + KW_ONLY dataclass, real fields read (`D(1, 9, y=3)`) | 4883 | 4 | rc=0 | rc=0 PROVED |
Scratch, not filed: `D(1, 2) == D(1, 3)` (CPython True: InitVar not compared) FAILS the Why3 type check at base and after (record
`==` unsupported) — not a false proof.
**Census / blast radius.** `__slots__`: 8 files in the corpora / mirrors / `pycsl_lib` (pyref 0079, corpus 0900 / 0901 / 0975,
mirrors Module1_Ingestor / Module2_Parser / pure_ast, `pycsl_lib/re/_engine.py`), none storing outside its slots; InitVar: 1 user
(corpus 4058, never read as an attribute; REFUSED at base by route #315, unchanged), KW_ONLY: 0, `super(X, self)`: 0; no
invariant-carrying dataclass with a pseudo-field. Root / pyref / mirror byte-diffs 0 MOVED / 0 GONE / 0 APPEARED and the 4
`pycsl_lib` files with slots / dataclasses / `super(` give byte-identical `--no-proof` output base vs candidate: nothing newly refused.
**Gates** (logs in the executor scratchpad `r360/g/`; rc): witnesses / controls above (full proof via heavy.sh, base fcc2c822 vs
candidate); byte-diff-compare root rc=0 (2313 base / 2320 candidate: 0 MOVED / 0 GONE / 0 APPEARED, 7 new control sources), pyref
rc=0 (2186/2186 0/0/0, `--min-files 2000`), mirror rc=0 (53/53 0/0/0, `--min-files 50`: **no OWED proof**);
check-self-annotate-sync.sh rc=0 (926 verbatim); self-annotate-mirror-check.sh rc=0 (53); check-getattr-erasure rc=0;
check-stdlib-modules-verify @@STDLIB@@; run-soundness-planes.sh fast **61/61** rc=0; `--slow` NOT run; doc-coherency --check rc=0;
check-assumed-facts rc=0 (85 facts, all reviewed families); check-dropped-mutation rc=0 (0 / 51 / 5 / 0); check-refusal-witness-coverage
rc=0 (300 demonstrated / 5 not, ceiling 5; rows 4850-4869 via `_census_row`); check-trusted-reasons rc=0 (420 / 420);
check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3, HOLE 0);
check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) By-NAME over-approximation: an attribute of the same name on any receiver is refused (0 users), including
`self.k = k` in `__post_init__` (store the value under another name). (2) An imported dataclass's pseudo-fields are not seen
(per-file). (3) The record type still carries the pseudo-fields (no emission change); no access to them survives the rule.
