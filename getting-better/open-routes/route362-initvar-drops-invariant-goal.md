# OPEN ROUTE #362 — AN `InitVar` MAKES DATACLASS CONSTRUCTION OPAQUE AND DROPS THE INVARIANT GOAL
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r360 executor off fcc2c822 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r362/`: `r07_initvar_post_init_inherited_import.py`, `r45_invariant_initvar_nodefault.py`.

With an InitVar the construction becomes opaque (as route #150 does for `__post_init__`) and no constructor-invariant goal is stated, so `invariant x >= 0` is assumed for every instance; CPython -1. Controls without InitVar / with defaults / init=False / kw_only / a verified `D(-5)` FAIL correctly.

Repair: Extend R346: refuse an invariant-carrying dataclass whose base closure declares any InitVar (or keep the construction non-opaque so the goal is stated).

## REPAIR (2026-10-25, r360 executor off fcc2c822; code 6550de83, corpus eae6a9d8 + dea007f9, census 69d1e9f2, docs 5be7bed4 + route docs)
**Design: sound refusals plus a sharper #347 summary, no emission change** — inline additions to the #346-#349 block of
`_run_pipeline` (mirror twin `\trusted`; no new def; ledger 3), shared by routes #360-#363 (annotations §7.32, translational
§T.6.43). New shared facts: each `@dataclass`'s InitVar / KW_ONLY pseudo-fields, each class's literal `__slots__`, and each
class's C3 MRO over the file's classes (an outside base is a leaf).
**Why a refusal.** The constructor goal `_check_class_inv_<C>` (route #226) is stated only over `int` fields and `int` / `bool`
parameters (`preamble.py`: `_ci_ptypes` in `("", "int", "bool")`); an `InitVar[T]` parameter, or the `_: KW_ONLY` sentinel field
(type `KW_ONLY`), puts a synthesized dataclass constructor outside it and the goal is silently dropped (measured: without the
InitVar the same class emits `goal _check_class_inv_d : forall x : int. x = x -> ((x >= 0))`, which FAILS correctly; with it, no
goal). Keeping the construction in scope would need the pseudo-field out of the record / signature typing (an emission change)
and the goal would then FAIL anyway for an invariant over an `__init__` parameter; the census finds 0 invariant-carrying
dataclasses with a pseudo-field. RULE `PYCSL-R362-INITVAR-INVARIANT` (extends R346): a record with merged `class_invariants` whose
base closure holds a `@dataclass` declaring an `InitVar` or `KW_ONLY` pseudo-field is REFUSED.
**Probe table** (full pycsl proof via heavy.sh; base = fcc2c822):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| r07 defaulted InitVar, `f(D(-1))` | 4865 | -1 | rc=0 PROVED | rc=1 REFUSED R362 |
| r45 InitVar without default, `f(D(-1, 0))` | 4866 | -1 | rc=0 PROVED | rc=1 REFUSED R362 |
| (new) `_: KW_ONLY` sentinel, `f(D(-1))` | 4867 | -1 | rc=0 PROVED | rc=1 REFUSED R362 |
| control: InitVar dataclass WITHOUT an invariant, `no_exception` read of `d.x` | 4884 | 1 | rc=0 | rc=0 PROVED |
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
**Residuals — NEW SUSPECTED FALSE PROOFS (same mechanism, NOT this route's shape, not repaired).** The goal is dropped for ANY
constructor outside route #226's scope, and the invariant is then assumed: measured PROVED at base AND after, CPython -1 —
`@dataclass` `x: int; s: str` + `invariant x >= 0` (`q362str`), `@dataclass` `x: int; xs: List[int] = field(default_factory=list)`
(`q362list`), and an EXPLICIT `__init__(self, x: int, xs: List[int])` storing both (`q362xinit`) (repro:
`<executor scratchpad>/r360/q/q362{str,list,xinit}.py`). route226's census counts 96 corpus classes "out of scope, non-int field",
so a refusal would not be inert: this needs its own route (state the goal over the int fields with the others universally
quantified, or refuse an invariant whose goal is not emitted). A non-dataclass `__init__(self, x: int, s: float)` does get its
goal (FAILS correctly).
