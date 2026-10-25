# OPEN ROUTE #349 — A SET LITERAL / DICT KEY OF AN UNHASHABLE RECORD PROVES no_exception
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r346 executor off b83a217b — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r349/`: `e08_record_hash_dict.py`, `e09_dataclass_unhashable_set.py`.

`@dataclass` (eq=True implies `__hash__ = None`) or an explicit `__hash__ = None`; `s = {d}` under `no_exception` PROVES (emission `let s = ref (any int)`); CPython TypeError unhashable. (e10 dict key: Why3 mutable-type error; e11 raising `__hash__`: FAIL.)

Repair: Refuse unhashable records (eq-dataclass without frozen/unsafe_hash, explicit `__hash__ = None`, `__eq__` without `__hash__`) as set elements / dict keys / hash arguments.

## REPAIR (2026-10-25, r346 executor off b83a217b; code 2054301b, corpus + docs ff6941ee, census 44f8d480 + route docs)
**Design: sound refusal, no emission change** — one inline block appended to the #341/#342 block of `_run_pipeline` (mirror twin
`\trusted`; no new def; ledger 3), shared by routes #346-#349 (annotations §7.28, translational §T.6.39). Base closure: each class's
in-file base names, left-to-right depth-first (an over-approximation of the MRO's class set).
**Why a refusal.** A set / dict of records is already an opaque value (`any int`); modelling `__hash__` would add a hashability
predicate on every hashing site for a shape the census shows unused (0 users). RULE `PYCSL-R349-UNHASHABLE-RECORD`: unhashable
classes decided as Python does, per class along the base closure (own `__hash__ = None` -> unhashable; own `__hash__` ->
hashable; `@dataclass` `unsafe_hash` -> hashable, else `eq` (default) -> hashable iff `frozen`; own `__eq__` without `__hash__`
-> unhashable; else inherited, `list` / `dict` / `set` / `bytearray` bases unhashable; a NamedTuple / frozen record with a
`list` / `dict` / `set` / unhashable-record field also unhashable). Refused: an expression of such a class (a typed name, `self`,
a constructor call, a typed field) as a set / set-comprehension element, dict / dict-comprehension key, subscript index,
`hash(..)` argument, `set(..)` / `frozenset(..)` / `Counter(..)` / `fromkeys(..)` element, `in` / `not in` against anything but a
list / tuple, or `.add` / `.discard` / `.remove` / `.get` / `.setdefault` / `.pop` argument on a receiver not known to be a list;
and any annotation `Set[U]` / `Dict[U, ..]` / `Mapping[U, ..]` / ... with `U` unhashable (such a value cannot exist).
**Probe table** (full pycsl proof via heavy.sh; base = b83a217b):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| e08 explicit `__hash__ = None`, `{r}` | 4678 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| e09 eq-dataclass `{d}` | 4679 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| (new) `__eq__` without `__hash__`, `{r}` | 4680 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| (new) dict key `{d: 1}` (= e10) | 4681 | TypeError | rc=1 FAILED (Why3 mutable-type error) | rc=1 REFUSED R349 |
| (new) `hash(d)` | 4682 | TypeError | rc=1 FAILED (Why3 type error) | rc=1 REFUSED R349 |
| (new) `{D(1)}` | 4683 | TypeError | rc=1 FAILED (Why3 type error) | rc=1 REFUSED R349 |
| (new) `s: Set[D]; s.add(d)` | 4684 | TypeError | rc=1 FAILED (Why3 type error) | rc=1 REFUSED R349 (annotation) |
| (new) `d in {D(2)}` | 4685 | TypeError | rc=1 FAILED (Why3 type error) | rc=1 REFUSED R349 |
| controls: explicit `__hash__` 4694; frozen dataclass 4695; plain class (identity hash) 4696 | 4694-4696 | ok | rc=0 | rc=0 PROVED |
Scratch, not filed: `d in xs` with `xs: List[D]` is not refused (equality only) and FAILS at base and after (Why3 typing of a
record list, pre-existing).
**Census / blast radius.** Before landing, every class-bearing file of the root corpus, pyref, the 53 mirrors and `pycsl_lib`
(1286 files) was screened `--no-proof` with the candidate: **0 hits outside the new witnesses** (no latent false proof in the
corpora; nothing newly refused). Root / pyref / mirror byte-diffs 0 MOVED / 0 GONE / 0 APPEARED (below).
**Gates** (logs in the executor scratchpad; rc): witnesses / controls above (full proof via heavy.sh, base b83a217b vs
candidate); byte-diff-compare root rc=0 (2289 base / 2300 candidate: 0 MOVED / 0 GONE / 0 APPEARED, 11 new control sources),
pyref rc=0 (2192/2192 0/0/0, `--min-files 2000`), mirror rc=0 (53/53 0/0/0, `--min-files 50`: **no OWED proof**) — the first
parallel sweep showed 2 root GONE (4280/4281 shadow-import) and 5 pyref MOVED + 1 GONE (stdlib/json drivers): each re-emitted
singly is byte-identical base vs candidate (the json driver's verdict depends on the CWD — a `json/` directory at the repo root —
identically in both trees), i.e. parallel-sweep / CWD artefacts, not movers; check-self-annotate-sync.sh rc=0 (926 verbatim);
self-annotate-mirror-check.sh rc=0 (53); check-getattr-erasure rc=0; check-stdlib-modules-verify @@STDLIB@@; run-soundness-planes.sh
fast @@PLANES@@; doc-coherency --check rc=0; check-assumed-facts rc=0 (ledger 3); check-dropped-mutation rc=0 (0 / 51 / 5 / 0);
check-refusal-witness-coverage rc=0 (293 demonstrated / 5 not, ceiling 5; rows 4660-4685 via `_census_row`); check-trusted-reasons
rc=0 (420 / 420); check-trusted-raises-honesty rc=0 (19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3,
HOLE 0); check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) Elements whose class is not derivable from annotations / constructor calls / typed fields (a callee's return,
a container element, an untyped local) are not checked. (2) Hashability of NamedTuple / frozen fields is checked one level (an
`Optional[List[int]]` field, a nested tuple of lists are missed). (3) A hashable record with a raising user `__hash__` is route
#349's e11 shape (FAILS at base, unchanged). (4) Imported unhashable classes are not seen (per-file).
