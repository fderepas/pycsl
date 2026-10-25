# OPEN ROUTE #371 — HASHABILITY FOLLOWS ONLY THE FIRST BASE
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r369 executor off dc378283 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r371/`: `h22_mixin_hash_none_second_base.py`, `h56_mixin_eq_second_base.py`, `h60_mixin_second_base_dc_eq.py`, `h63_mixin_third_base.py`, `h64_mixin_via_intermediate_second.py`, `h67_second_base_frozen_field.py`.

The inherited `__hash__` / `__eq__` lookup follows `bases[0]` only: `D(N, M)` with an unhashable mixin M is treated as hashable (control `D(M)` is refused). Slips past #364/#349. CPython TypeError unhashable.

Repair: Look up `__hash__` / `__eq__` along the full C3 MRO.

## REPAIR (2026-10-25, r369 executor off dc378283; code 88877615 / 6b575c0e / 38161b2e / 5a70413a / c2f46d20 / 710d3223, docs 2623c62a (annotations §7.35 / translational §T.6.46), corpus c2f46d20 + 710d3223, census 001405cc + 710d3223, route docs)
**Design (shared by #369-#372): sound refusals, no emission change, no new def** (inline in the #346-#349 / #360-#363 block and the
#339/#352 enum block of `_run_pipeline`, mirror twin `\trusted`), ledger 3. Two new refusal codes, `PYCSL-R369-DATACLASS-SPECIFIER` and
`PYCSL-R369-CONSTRUCTOR-ARITY`; #370 reuses `PYCSL-SEM-ENUM-MEMBER-OPERATION`, #371 / #372 reuse `PYCSL-R349-UNHASHABLE-RECORD`
(annotations §7.35, translational §T.6.46).
RULE (in route #349's hashability fixpoint, #364/#366 unchanged). `__hash__` is looked up along the C3 MRO (`_mro363`): the
first class whose own scope decides (an own `__hash__` binding per #364, the `@dataclass` options, an own `__eq__` — which sets
`__hash__ = None` in that class) wins; a functional-namedtuple ancestor decides by its fields; `list` / `dict` / `set` / `bytearray`
are unhashable; other outside bases are skipped; a class whose linearisation is unknown counts as unhashable. The old walk stopped
at the first base already decided (`N`: hashable), so the mixin's `__hash__ = None` was never reached.
**Probe table** (full pycsl proof via heavy.sh; base = dc378283 worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| h22 `D(N, M)`, `M.__hash__ = None` | 5025 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h56 `D(N, M)`, `M.__eq__` | 5026 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h60 `D(N, M)`, eq-dataclass `M` | 5027 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h63 `D(N, O, M)` | 5028 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h64 `D(P)`, `P(N, M)` | 5029 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| h67 frozen `D` with `z: Z`, `Z(N, M)` | 5030 | TypeError | rc=0 PROVED | rc=1 REFUSED PYCSL-R349-UNHASHABLE-RECORD |
| control: `D(N, M)` with `N.__hash__` first in the MRO (M unhashable) | 5043 | ok | rc=0 PROVED (first base) | rc=0 PROVED |
Controls 5040-5044 PROVED at base and after (regression controls; no over-refusal existed at base). The census run (`_census_row`,
full pipeline) of every FAIL witness 4990-5039 / 5045 at the final candidate records REFUSAL for all 51.
**Census / blast radius** (shared): before landing, 497 `@dataclass` classes / 1000 annotated members / 103 `field(..)` calls over
both corpora, the 53 mirrors and `pycsl_lib` were resolved by a prototype of rule (a): 0 aliases, 0 unknown heads once a
module-level string alias (`Expr = "Leaf | Bad"`), an int stub alias (`Term = 0`) and an unbound forward name are read as
non-specifiers. The first candidate sweep showed 15 root GONE (0950-0965 string-alias heads, 4942 `p: "P"`): a string annotation
parsed twice gave a fresh node whose resolution was looked up under the wrong id, plus a variable-name clash in the arity block
(`'bool' object has no attribute 'get'`); fixed in 5a70413a, re-emitted byte-identical, re-swept to 0/0/0. Final sweeps (code
710d3223): root 2341 base / 2346 candidate .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new control sources); pyref 2186 / 2186 0/0/0
(`--min-files 2000`); mirror-emit-sweep 53 / 53 0/0/0 (`--min-files 50`) — **no OWED proof**. So 0 non-witness users of any newly
refused shape in any plane, including the arity check over explicit `__init__`s.
**Gates** (logs in the executor scratchpad; rc): witnesses / controls above (full proof via heavy.sh, base dc378283 worktree vs
candidate); byte-diff-compare root rc=0, pyref rc=0, mirror rc=0 (above); check-self-annotate-sync.sh rc=0 (926 verbatim);
self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast **61/61** rc=0 (`--slow` NOT run); check-getattr-erasure rc=0
(DECLARED 0); check-stdlib-modules-verify rc=0 (one command via heavy.sh: 104 modules, 83 VERIFY, the known 21 non-verifying); doc-coherency --check rc=0; check-assumed-facts rc=0 (85 facts, all reviewed families; ledger 3);
check-dropped-mutation rc=0 (0 / 51 / 5 / 0); check-refusal-witness-coverage rc=0 (303 demonstrated / 5 undemonstrated = ceiling
5; rows 4990-5039 + 5045 via `_census_row`); check-trusted-reasons rc=0 (420 / 420, ratchet 259); check-trusted-raises-honesty rc=0
(19 / 61, ratchet 61); check-assigns-underdeclaration --transitive rc=0 (TRAP 3, HOLE 0); check-mirror-coverage rc=0 (549 / 41).
**Residuals.** (1) Outside bases (imported classes) are skipped in the lookup: an imported unhashable mixin is not seen
(per-file, #349 residual 4). (2) `__hash__ = object.__hash__` restores remain over-refused (#364 residual).
