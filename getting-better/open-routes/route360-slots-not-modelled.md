# OPEN ROUTE #360 — `__slots__` IS NOT MODELLED — A STORE OUTSIDE THE SLOTS PROVES
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r360 executor off fcc2c822 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r360/`: `a12_slots_store_unslotted.py`, `s02_slots_inherited_extra.py`, `s05_empty_slots_init_store.py`, `s06_slots_init_param.py`, `s08_slots_list_form.py`.

A constructor / method store of a name outside the union of `__slots__` over the MRO is lowered as an ordinary record field store (tuple, list, empty and inherited slots forms); CPython raises AttributeError at construction.

Repair: Compute the slots union over the MRO; when every in-file MRO class declares `__slots__`, refuse a `self.f` / `r.f` store whose name is outside it; refuse non-literal `__slots__`.

## REPAIR (2026-10-25, r360 executor off fcc2c822; code 6550de83, corpus eae6a9d8 + dea007f9, census 69d1e9f2, docs 5be7bed4 + route docs)
**Design: sound refusals plus a sharper #347 summary, no emission change** — inline additions to the #346-#349 block of
`_run_pipeline` (mirror twin `\trusted`; no new def; ledger 3), shared by routes #360-#363 (annotations §7.32, translational
§T.6.43). New shared facts: each `@dataclass`'s InitVar / KW_ONLY pseudo-fields, each class's literal `__slots__`, and each
class's C3 MRO over the file's classes (an outside base is a leaf).
**Why a refusal.** A faithful model would give slotted records a closed attribute set and an AttributeError branch on
every other store; refusing the store is local, and the census finds no store outside the slots anywhere. RULE
`PYCSL-R360-SLOTS-STORE`: slots are read from a literal class-body `__slots__` (a string = ONE slot; a tuple / list / set of
strings; a dict with string keys) or `@dataclass(slots=True)` (its annotated fields); any other `__slots__` binding is REFUSED.
A class is FULLY SLOTTED when every class of its C3 MRO is a file class declaring slots, or `object` / `Generic` / `Protocol`,
and no slot is `__dict__`. At every store site of route #348 (attribute store / augmented / `del` / `for` / `with` target,
`setattr` / `delattr`; non-literal name = any) whose receiver may be a fully slotted class (`self` of one of its methods — not a
`classmethod`'s `cls` —, a name annotated with / constructed as one, a typed field), a name outside the union of the slots over
the MRO is REFUSED.
**Probe table** (full pycsl proof via heavy.sh; base = fcc2c822):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| a12 `("x",)`, `__init__` stores `self.y` | 4850 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| s02 `B(A)` both slotted, `self.z` | 4851 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| s05 `__slots__ = ()` | 4852 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| s06 `self.b = v` from a parameter | 4853 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| s08 list form | 4854 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| (new) external `r.y = 1` on `r: R` | 4855 | AttributeError | rc=1 FAILED | rc=1 REFUSED R360 |
| (new) `setattr(self, "y", 1)` | 4856 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| (new) `__slots__ = SL` (non-literal) | 4857 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| (new) `__slots__ = "x"` (one slot) | 4858 | AttributeError | rc=0 PROVED | rc=1 REFUSED R360 |
| (new) `@dataclass(slots=True)`, method stores `self.z` | 4859 | AttributeError | rc=1 FAILED | rc=1 REFUSED R360 |
| controls: in-slot stores own + inherited 4880; `"__dict__"` slot 4881; slotted subclass of a plain base 4882 | 4880-4882 | ok | rc=0 | rc=0 PROVED |
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
**Residuals.** (1) A receiver of unknown class (un-annotated name, container element) is not checked. (2) An imported base is
treated as providing a `__dict__` (not fully slotted): a file class over an imported slotted base is not checked. (3) A
`__slots__` bound under control flow in the class body is not read. (4) Over-refusal: a store through a property setter / data
descriptor named outside the slots (0 users).
