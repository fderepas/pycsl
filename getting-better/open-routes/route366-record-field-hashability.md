# OPEN ROUTE #366 — HASHABILITY OF IMMUTABLE-RECORD FIELDS IS COMPUTED IN ONE ORDERED PASS AND MISSES object/Any/unsafe_hash
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r364 executor off fcc2c822 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r366/`: `h08_frozen_object_field.py`, `h23_unsafe_hash_list_field.py`, `h24_frozen_field_forward_ref_order.py`, `h25_frozen_field_forward_ref_dc.py`, `h27_frozen_tuple_field_of_dc.py`, `h31_namedtuple_object_field.py`.

A field class declared later (`z: "Z"`, h24/h25) is missed by the single name-ordered pass; `object` / `Any` fields accept any value (h08, h31); `unsafe_hash=True` records are never field-checked (h23); `Tuple[Z, int]` contributes only its head (h27). CPython TypeError (unhashable list / record field).

Repair: Fixpoint over all classes; `object` / `Any` / unknown field annotations and every Tuple/Union argument possibly unhashable; field check applies to unsafe_hash records.

## REPAIR (2026-10-25, r364 executor off fcc2c822; code e78477a2 + 396b6ebb, corpus + docs ece5f63b (annotations §7.33 / translational §T.6.44), census 694d2e7c, route docs)
**Design (shared by #364-#367): sound refusals, no emission change, no new def (inline in the #346-#349 and the #339/#352 blocks of `_run_pipeline`, mirror twin `\trusted`), ledger 3, no new refusal code** (`PYCSL-R349-UNHASHABLE-RECORD`, `PYCSL-SEM-ENUM-MEMBER-OPERATION`).
RULE (#366): unhashability is the least FIXPOINT over every class and functional namedtuple of the file (iterated until stable;
a non-converging bound would mark every class unhashable), so a field class declared later is seen. A record whose hash hashes
its fields — NamedTuple / `namedtuple` / `NamedTuple(..)`, a frozen or `unsafe_hash=True` `@dataclass`, or a subclass of one —
is unhashable unless EVERY field annotation along its base closure is provably hashable: `int` / `str` / `float` / `bool` /
`bytes` / `complex` / `None` / `Literal[..]` / `frozenset[..]` / `type[..]`, a hashable file class, or an Optional / Union /
`|` / Tuple / Annotated / Final / ClassVar of those. `object`, `Any`, a TypeVar, an imported or unknown class, any other
container (`List`, `Sequence`, `Mapping`, `Callable` ...) and an untyped `namedtuple` field are possibly unhashable.
**Probe table** (full pycsl proof via heavy.sh; base = fcc2c822 worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| h08 frozen `xs: object` | 4913 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h23 `unsafe_hash=True`, `List[int]` field | 4914 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h24 frozen `z: "Z"`, NamedTuple `Z` (list field) declared after | 4915 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h25 frozen `z: "Z"`, eq-dataclass `Z` declared after | 4916 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h27 frozen `zs: Tuple[Z, int]` | 4917 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h31 NamedTuple `xs: object` | 4918 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| NEW shape: frozen `v: Union[int, List[int]]` | 4919 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| NEW shape: NamedTuple `v: Any`, `hash(n)` | 4920 | TypeError | rc=1 FAILED | rc=1 REFUSED R349 |
| control: frozen int / Optional[float] / forward NamedTuple / Tuple[int, ...] / FrozenSet fields; unsafe_hash int field | 4942 | ok | rc=0 PROVED | rc=0 PROVED |
**Census / blast radius** (shared): the candidate was swept over every plane before landing — root 2314 base / 2318 candidate .mlw: 0 MOVED / 0 GONE / 0 APPEARED (4 new controls); pyref 2186/2186 0/0/0; mirror-emit-sweep 53/53 0/0/0 (`--min-files 50`) — no OWED proof. The first candidate sweep showed 4 root GONE (1853, 1854, 1878, 2586: a `Callable[[int], int]` ANNOTATION inside a function was walked as a subscript hashing a tuple holding a list); fixed in 396b6ebb (annotation subtrees hash nothing) and re-swept to 0/0/0. So 0 non-witness users of any newly refused shape in any plane.
**Gates** (one run for #364-#367 on the final code, all rc 0; logs in the executor scratchpad): witnesses / controls above (full
proof via heavy.sh, base fcc2c822 vs candidate; final code re-screened `--no-proof`: 36 refused / 4 controls emit);
byte-diff-compare root rc=0 (2314 / 2318, 0/0/0, 4 new controls), pyref rc=0 (2186 / 2186, 0/0/0, `--min-files 2000`), mirror
rc=0 (53 / 53, 0/0/0, `--min-files 50`: no OWED proof); check-self-annotate-sync.sh (926 verbatim); self-annotate-mirror-check.sh
(53); run-soundness-planes.sh fast 61/61 (`--slow` NOT run); check-getattr-erasure (DECLARED 0); check-stdlib-modules-verify (104
modules, 83 VERIFY, non-verifying set = the known 21); doc-coherency --check; check-assumed-facts (85 facts, all reviewed; ledger
3); check-dropped-mutation (0 / 51 / 5 / 0); check-refusal-witness-coverage (296 demonstrated / 5 undemonstrated = ceiling 5; rows
4900-4933 via `_census_row`); check-trusted-reasons (420 / 420, ratchet 259); check-trusted-raises-honesty (19 / 61, ratchet 61);
check-assigns-underdeclaration --transitive (TRAP 3, HOLE 0); check-mirror-coverage (549 / 41).
**Residuals.** Over-refusal: a `field(hash=False)` / `compare=False` field, a frozen dataclass with `eq=False` (identity hash)
or with its own `def __hash__` is still field-checked; an imported hashable class (`Decimal`, `Path`) as a field type is
refused (0 users measured). Imported records are not inspected (per-file, route #349 residual (4)).
