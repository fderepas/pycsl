# OPEN ROUTE #364 — #349's CLASS-BODY HASHABILITY SCAN SEES ONLY `def __eq__` AND LITERAL `__hash__ = None`
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r364 executor off fcc2c822 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r364/`: `h01_eq_lambda_assign_set.py`, `h02_hash_none_via_name.py`, `h21_hash_none_ifexp.py`, `h22_eq_under_if.py`, `h33_hash_none_tuple_assign.py`.

Missed: `__eq__ = lambda ...` (h01), `__hash__ = NOHASH` (h02), `__hash__ = None if ... else ...` (h21), `__eq__` under `if` (h22), `__hash__, tag = None, 1` (h33); a set element of such a record proves under no_exception; CPython TypeError unhashable.

Repair: Any class-body binding of `__eq__` (any statement / nesting) defines it; a `__hash__` binding to anything but a def is 'maybe None' => unhashable.

## REPAIR (2026-10-25, r364 executor off fcc2c822; code e78477a2 + 396b6ebb, corpus + docs ece5f63b (annotations §7.33 / translational §T.6.44), census 694d2e7c, route docs)
**Design (shared by #364-#367): sound refusals, no emission change, no new def (inline in the #346-#349 and the #339/#352 blocks of `_run_pipeline`, mirror twin `\trusted`), ledger 3, no new refusal code** (`PYCSL-R349-UNHASHABLE-RECORD`, `PYCSL-SEM-ENUM-MEMBER-OPERATION`).
RULE (#364): the hashability scan of route #349 reads every binding of the CLASS SCOPE (any statement, any target form, any
nesting — `if` / `try` / `with` / `for` —, an import, a `del`, a match / except capture; nested `def` / `class` / `lambda` bodies
are other scopes): any binding of `__eq__` defines it, and a class that binds `__hash__` is hashable only when EVERY binding of it
is a top-level undecorated `def __hash__`; any other binding (a name, an if-expression, a tuple target, an assignment of
`object.__hash__`) may be None and the class counts as unhashable (the refusing direction). Then route #349's order (dataclass
options, own `__eq__`, inheritance) decides as before.
**Probe table** (full pycsl proof via heavy.sh; base = fcc2c822 worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| h01 `__eq__ = lambda ..`, `{r}` | 4900 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h02 `__hash__ = NOHASH` | 4901 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h21 `__hash__ = None if True else ..` | 4902 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h22 `def __eq__` under `if True:` | 4903 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h33 `__hash__, tag = None, 1` | 4904 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| NEW shape: `__eq__, tag = (lambda ..), 1` | 4905 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| control: `__eq__` under `if` + top-level `def __hash__` | 4940 | ok | rc=0 PROVED | rc=0 PROVED |
| over-refusal probe (not filed): `__hash__ = object.__hash__` after `def __eq__` | — | ok | rc=0 PROVED | rc=1 REFUSED |
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
**Residuals.** Over-refusal: `__hash__ = object.__hash__` / `Base.__hash__` (a hashable restore) and a decorated or
conditionally defined `def __hash__` are read as maybe-None (0 users measured; write a plain `def __hash__`). A class body that
binds through `locals()` / `vars()` / `exec` is not seen. Route #349's residuals (1), (3), (4) stand.
