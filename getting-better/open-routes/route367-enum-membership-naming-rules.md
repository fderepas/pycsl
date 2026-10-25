# OPEN ROUTE #367 — ENUM MEMBERSHIP IGNORES `_ignore_` AND PRIVATE-NAME RULES
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r364 executor off fcc2c822 — sound refusal, see REPAIR). Was OPEN, Severity 1.** Red-team round 27 (2026-10-25, probes around the #346-#356 repairs); driver-reproduced on main ccdb07e6 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt27/driver-repro.txt`).
Witnesses `witnesses-r367/`: `e18_ignore.py`, `e29_ignore_attr.py`, `e30_private_name_not_member.py`, `e33_ignore_string_form.py`.

Names listed in `_ignore_` (list or string form) and private `__B` names are treated as members by routes #355/#356: `C(2)`, `C(1)`, `C.B` admitted; CPython ValueError / AttributeError.

Repair: Build the member set as Enum does: drop `_ignore_` names (refuse a non-literal `_ignore_`), private `__x`, sunder/dunder names, descriptors and `nonmember(...)`.

## REPAIR (2026-10-25, r364 executor off fcc2c822; code e78477a2 + 396b6ebb, corpus + docs ece5f63b (annotations §7.33 / translational §T.6.44), census 694d2e7c, route docs)
**Design (shared by #364-#367): sound refusals, no emission change, no new def (inline in the #346-#349 and the #339/#352 blocks of `_run_pipeline`, mirror twin `\trusted`), ledger 3, no new refusal code** (`PYCSL-R349-UNHASHABLE-RECORD`, `PYCSL-SEM-ENUM-MEMBER-OPERATION`).
RULE (#367): the member set is built as `enum._EnumDict` builds it. A top-level class-body binding is a member unless its name is
in `_ignore_` (a literal string split on commas / blanks, or a list / tuple of strings), private (`__x` not ending `__`:
mangled, a plain attribute since 3.11), a CPython dunder / sunder (`_is_dunder` / `_is_sunder`), an annotation without value
(binds nothing), or its value is a descriptor (`def`, `class`, `lambda`, an unshadowed builtin `property(..)` /
`classmethod(..)` / `staticmethod(..)`) or `nonmember(..)` (resolved through `from enum import` / `enum.`); `member(v)` is a
member of value `v`. Ignored, private and value-less names are not class attributes either, so `C.B` / `C.__B` are refused
(route #356's rule). An `_ignore_` that is not ONE top-level binding to such a literal (a name, a nested or tuple-target binding)
makes the member set unknown and is REFUSED. The enum's user dunders and `__new__` are read from every class-scope binding
(route #364's rule): NEW latent false proofs, `if True: def __eq__` and `__eq__, _x = (lambda ..), 0` on an enum PROVED
`x == x` True (CPython False).
**Probe table** (full pycsl proof via heavy.sh; base = fcc2c822 worktree):
| witness | corpus | CPython | base | after |
|---|---|---|---|---|
| e18 `_ignore_ = ["B"]`, `C(2)` | 4921 | ValueError | rc=0 PROVED | rc=1 REFUSED |
| e29 `_ignore_ = ["B"]`, `x = C.B` | 4922 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| e30 `__B = 1`, `C(1)` | 4923 | ValueError | rc=0 PROVED | rc=1 REFUSED |
| e33 IntEnum `_ignore_ = "B"`, `C(2)` | 4924 | ValueError | rc=0 PROVED | rc=1 REFUSED |
| NEW shape: `_ignore_ = ("B",)` | 4925 | ValueError | rc=0 PROVED | rc=1 REFUSED |
| NEW shape: `_ignore_ = NAMES` (non-literal), `C(1)` | 4926 | ok (refusal by design) | rc=0 PROVED | rc=1 REFUSED |
| NEW shape: `x = C.__B` | 4927 | AttributeError | rc=0 PROVED | rc=1 REFUSED |
| NEW shape: `_ignore_` under `if True:`, `C(2)` | 4928 | ValueError | rc=0 PROVED | rc=1 REFUSED |
| NEW shape: IntEnum `_ignore_ = "B, D"`, `C(4)` | 4929 | ValueError | rc=0 PROVED | rc=1 REFUSED |
| NEW shape: `B: int` (no value), `x = C.B` | 4930 | AttributeError | rc=1 REFUSED (R325) | rc=1 REFUSED |
| NEW latent: enum `if True: def __eq__`, `x == x` | 4931 | violates | rc=0 PROVED | rc=1 REFUSED |
| NEW latent: enum `__eq__, _x = (lambda ..), 0`, `x == x` | 4932 | violates | rc=0 PROVED | rc=1 REFUSED |
| NEW shape: `X = nonmember(3)`, `C(3)` | 4933 | ValueError | rc=1 REFUSED | rc=1 REFUSED |
| control: `_ignore_ = ["tmp"]`, `member(2)`, a lambda attribute: `C(1)`, `C(2)`, `C.A` | 4943 | ok | rc=1 REFUSED (over-refusal) | rc=0 PROVED |
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
**Residuals.** Members bound by a tuple target or under a compound statement (`A, B = 1, 2`, `for _i in ..`) are not seen
as members (their `C(v)` / `C.A` is refused: over-refusal, sound). A descriptor bound through a name (`f = helper`) or an
unknown call stays a member of unknown value (`C(v)` refused). `_missing_` / `_generate_next_value_` / `auto()` keep route
#355's refusals.
