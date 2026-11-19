# OPEN ROUTE #365 — AN UNHASHABLE RECORD INSIDE A TUPLE IN A HASHING POSITION IS NOT CHECKED
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r364 executor off fcc2c822 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r365/`: `h15_unhashable_in_tuple_set.py`, `h16_tuple_hash.py`, `h26_tuple_elem_set_typed.py`, `h29_dict_tuple_key.py`.

`{(d, 1)}`, `hash((d, 2))`, `{t}` with `t: Tuple[D, int]`, `{(d, 1): 0}`: only the element expression itself is checked; CPython TypeError unhashable.

Repair: In every hashing position recurse into tuple displays and `Tuple[...]` annotation arguments.

## REPAIR (2026-10-25, r364 executor off fcc2c822; code e78477a2 + 396b6ebb, corpus + docs ece5f63b (annotations §7.33 / translational §T.6.44), census 694d2e7c, route docs)
**Design (shared by #364-#367): sound refusals, no emission change, no new def (inline in the #346-#349 and the #339/#352 blocks of `_run_pipeline`, mirror twin `\trusted`), ledger 3, no new refusal code** (`PYCSL-R349-UNHASHABLE-RECORD`, `PYCSL-SEM-ENUM-MEMBER-OPERATION`).
RULE (#365): in every hashing position of route #349 (set display / comprehension element, dict key, subscript index, `hash(..)`,
`in` against a non-list, `set` / `frozenset` / `Counter` / `fromkeys` element, `.add` / `.discard` / `.remove` / `.get` /
`.setdefault` / `.pop` argument, a `Set[..]` / `Dict[..]` / ... annotation) the class set of the hashed expression is computed
COMPONENTWISE: a tuple display is entered at any depth (also through `:=` and both arms of `x if c else y`), a name contributes
the classes of its annotations through every `Tuple[...]` / `tuple[...]` argument (through Optional / Union / `|` / string forms)
and of every value bound to it (a tuple display bound to a local, closed to a fixpoint over the bindings), and a list / dict /
set display or a list / dict / set-annotated name INSIDE a hashed tuple counts as unhashable (`#UB`; a top-level list is
already a Why3 type error and is not touched). Annotation subtrees inside a function (`Callable[[int], int]`) are not hashing
positions.
**Probe table** (full pycsl proof via heavy.sh; base = fcc2c822 worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| h15 `{(d, 1)}` | 4906 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h16 `t = (d, 2); hash(t)` | 4907 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h26 `t: Tuple[D, int]; {t}` | 4908 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| h29 `{(d, 1): 0}` | 4909 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| NEW shape: `{((d, 1), 2)}` | 4910 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| NEW shape: `t: Optional[Tuple[int, D]]; hash(t)` | 4911 | TypeError | rc=1 FAILED | rc=1 REFUSED R349 |
| NEW latent: `xs: List[int]; {(xs, 1)}` (a list inside a tuple) | 4912 | TypeError | rc=0 PROVED | rc=1 REFUSED R349 |
| control: tuples of a hashable frozen record in set / `hash` / dict-key positions | 4941 | ok | rc=0 PROVED | rc=0 PROVED |
Scratch, not filed: `hash(xs)` with `xs: List[int]` FAILS at base and after (Why3 type error, pre-existing).
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
**Residuals.** Tuples reached through a container element (`for t in pairs`), a callee's return or an untyped local
bound to something other than a tuple display are not decomposed (route #349 residual (1)). A starred component
(`(*xs,)`) is not entered.
