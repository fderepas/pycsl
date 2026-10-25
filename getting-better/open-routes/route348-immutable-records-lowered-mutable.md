# OPEN ROUTE #348 — NamedTuple / collections.namedtuple / FROZEN DATACLASS ARE LOWERED AS MUTABLE RECORDS
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r346 executor off b83a217b — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r348/`: `d11_namedtuple_store.py`, `j02_namedtuple_mutation_alias.py`, `j03_frozen_dc_free_fn.py`, `j07_collections_namedtuple.py`.

Emission `type n = { mutable x: int; mutable y: int }` and `n.x <- 5`: any field store on these types proves under `no_exception`; CPython raises AttributeError / FrozenInstanceError. (j01 method store: Why3 type error; d08 frozen store in a method: FAILs on its postcondition — not by design.)

Repair: Refuse attribute stores (and setattr/delattr) on NamedTuple, namedtuple and frozen-dataclass records, or emit them as raising.

## REPAIR (2026-10-25, r346 executor off b83a217b; code 2054301b, corpus + docs ff6941ee, census 44f8d480 + route docs)
**Design: sound refusal, no emission change** — one inline block appended to the #341/#342 block of `_run_pipeline` (mirror twin
`\trusted`; no new def; ledger 3), shared by routes #346-#349 (annotations §7.28, translational §T.6.39). Base closure: each class's
in-file base names, left-to-right depth-first (an over-approximation of the MRO's class set).
**Why a refusal.** Emitting the records as immutable would change every NamedTuple / frozen emission (record fields lose
`mutable`; corpus and pyref movers) while the only behaviour to model for a store is "raises"; refusing the store is exact and
measured inert (0 stores on such records anywhere). RULE `PYCSL-R348-IMMUTABLE-RECORD-STORE`: immutable records = classes with a
`NamedTuple` base, `@dataclass(frozen=True)` (or a non-literal `frozen`), names bound by `namedtuple(..)` / functional
`NamedTuple(..)`, and every class whose base closure holds one. In every function / method body an attribute store, augmented
store, `del`, `for` / `with` target, or `setattr` / `delattr` call is REFUSED when its receiver is a name annotated with /
constructed as an immutable record or `self` in a method of one, or is of unknown class (not provably a mutable class of the file)
and the attribute is a field of an immutable record of the file (any name when a functional field list is not literal).
`object.__setattr__(self, ..)` (the frozen-dataclass `__post_init__` idiom, which CPython accepts) is not this rule's; it was
already refused at base by another check.
**Probe table** (full pycsl proof via heavy.sh; base = b83a217b):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| d11 NamedTuple parameter `n.x = 5` | 4669 | AttributeError | rc=0 PROVED | rc=1 REFUSED R348 |
| j02 local `n = N(1); n.x = 7` | 4670 | AttributeError | rc=0 PROVED | rc=1 REFUSED R348 |
| j03 frozen dataclass store | 4671 | FrozenInstanceError | rc=0 PROVED | rc=1 REFUSED R348 |
| j07 `collections.namedtuple` store | 4672 | AttributeError | rc=0 PROVED | rc=1 REFUSED R348 |
| (new) `n.x += 1` | 4673 | AttributeError | rc=0 PROVED | rc=1 REFUSED R348 |
| (new) `setattr(d, "x", 5)` frozen | 4674 | FrozenInstanceError | rc=1 REFUSED (setattr under no_exception) | rc=1 REFUSED R348 |
| (new) plain subclass of a frozen dataclass | 4675 | FrozenInstanceError | rc=0 PROVED | rc=1 REFUSED R348 |
| (new) `self.x = 5` in a frozen method (= j01/d08 shape) | 4676 | FrozenInstanceError | rc=1 FAILED (postcondition, not by design) | rc=1 REFUSED R348 |
| (new) functional `NamedTuple("P", [..])` | 4677 | AttributeError | rc=0 PROVED | rc=1 REFUSED R348 |
| controls: NamedTuple READ 4692; MUTABLE dataclass store 4693 | 4692-4693 | ok | rc=0 | rc=0 PROVED |
Scratch, not filed: `del d.x` on a frozen record is REFUSED at base by the attribute-`del` rule (unchanged).
**Census / blast radius.** Before landing, every class-bearing file of the root corpus, pyref, the 53 mirrors and `pycsl_lib`
(1286 files) was screened `--no-proof` with the candidate: **0 hits outside the new witnesses** (no latent false proof in the
corpora; nothing newly refused). Root / pyref / mirror byte-diffs 0 MOVED / 0 GONE / 0 APPEARED (below).
**Gates** (logs in the executor scratchpad; rc): witnesses / controls above (full proof via heavy.sh, base b83a217b vs
candidate); byte-diff-compare root rc=0 (2289 base / 2300 candidate: 0 MOVED / 0 GONE / 0 APPEARED, 11 new control sources),
pyref rc=0 (2192/2192 0/0/0, `--min-files 2000`), mirror rc=0 (53/53 0/0/0, `--min-files 50`: **no OWED proof**) — the first
parallel sweep showed 2 root GONE (4280/4281 shadow-import) and 5 pyref MOVED + 1 GONE (stdlib/json drivers): each re-emitted
singly is byte-identical base vs candidate (the json driver's verdict depends on the CWD — a `json/` directory at the repo root —
identically in both trees), i.e. parallel-sweep / CWD artefacts, not movers; check-self-annotate-sync.sh rc=0 (926 verbatim);
self-annotate-mirror-check.sh rc=0 (53); check-getattr-erasure rc=0; check-stdlib-modules-verify rc=0-equivalent (run in 5 foreground chunks with its own `classify` + BASELINE: 104 modules, 83 VERIFY, 0 newly not verifying, 0 baseline now verifying); run-soundness-planes.sh
fast **61/61** rc=0; `--slow` NOT run; doc-coherency --check rc=0; check-assumed-facts rc=0 (ledger 3); check-dropped-mutation rc=0 (0 / 51 / 5 / 0);
check-refusal-witness-coverage rc=0 (293 demonstrated / 5 not, ceiling 5; rows 4660-4685 via `_census_row`); check-trusted-reasons
rc=0 (420 / 420); check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3,
HOLE 0); check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) A receiver whose class is known only through an untyped container element / callee return is judged by field
NAME (stores of non-field attributes on such a receiver are missed: e.g. `xs[0].extra = 1` on a NamedTuple element). (2) Imported
immutable records are seen only by name of their fields if declared in this file. (3) `attrs` (`@attr.s(frozen=True)`) and other
frozen-class libraries are not recognised. (4) Mutating a mutable FIELD of an immutable record (`n.items.append(1)`) is legal
Python and unchanged.
