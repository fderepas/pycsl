# OPEN ROUTE #352 — AN ENUM WHOSE BASE IS AN IMPORT ALIAS (`from enum import Enum as E`) IS NOT RECOGNISED — MEMBERS KEEP INT LAWS
**Status: REPAIRED, candidate (gen #37, 2026-10-25; opened the same day), Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r352/`: `e01_enum_import_alias.py`, `e28_intenum_import_alias_eq.py`.

Route #339 classifies an enum by the base's spelled name / attribute tail; `from enum import Enum as E; class C(E)` (e01: `x - x` under no_exception proves, CPython TypeError) and `IntEnum as IE` with a user `__eq__` (e28: `x == x` proves True, CPython False) fall outside the list, so `C` is a plain class and its members are ints.

Repair: Resolve base names through the file's imports (`from enum import X as Y`, `import enum as e`); refuse a class whose base is an imported name the check cannot classify.

## REPAIR (2026-10-25, r352 executor off 1a9cfa42; code 46558356, corpus + census 0855e796, docs 9a2cbb48 (annotations §7.30 / translational §T.6.41), route docs)
**Design (shared by #352-#356): one rewrite of route #339's classifier inside the same inline `_run_pipeline` block, plus two
checks after its context walk; sound refusals only (`PYCSL-SEM-ENUM-MEMBER-OPERATION`, no new code), no emission change, no new
def (mirror twin `\trusted`), ledger 3.** CENSUS before landing (CPython `ast`, every plane): enum-bearing files are the #339
corpus witnesses 4590-4601, 4243 (`Color.RED.value`), the mirror's `pure_ast._Precedence(_enum.IntEnum)` via `import enum as
_enum` (resolved now: still transparent, its 52 uses are members), pyref `stdlib/enum/*` (no enum class), pycsl_lib 0; no
`IntFlag` / `Flag` / mixin / `__members__` / `C(v)` user anywhere; classes with an unclassifiable (non-stdlib) imported base:
18, of which 0 have a member-shaped body (1344's `m = lambda` is a method, excluded) — so the possibly-enum rule moves nothing.
RULE (#352): every class base is RESOLVED through the file's imports and module-level aliases (bound once) to a token — a stdlib
enum class (`from enum import X as Y`, `import enum as e` + `e.X`, a bare enum-class name), a file class, a builtin, a non-enum
stdlib import, `T:X` (an attribute whose tail is an enum class name but whose module is not `enum`: an enum of unknown origin,
OPAQUE), or UNKNOWN (a non-stdlib / relative import, an unbound name, an expression; a non-`enum` star import makes bare names
unknown-origin). A class whose ancestry holds UNKNOWN and whose body has a member-shaped binding is POSSIBLY an enum (built on
an imported member-less enum) and is treated as OPAQUE with every operator dunder assumed user-defined — the measured-free
alternative to refusing such classes (0 in every plane).
**Probe table** (full pycsl proof via heavy.sh; base = 1a9cfa42 worktree; witnesses under `witnesses-r352/`):
| witness | corpus | CPython | base (1a9cfa42) | after |
|---|---|---|---|---|
| e01 `from enum import Enum as E`, `x - x` under `no_exception \all` | 4750 | TypeError | PROVED | REFUSED |
| e28 `IntEnum as IE` + user `__eq__`, `x == x` proved True | 4751 | violates | PROVED | REFUSED |
| probe: module-level `E = Enum` alias base | — | TypeError | REFUSED (route #341 alias base) | REFUSED |
| control: `import enum as e; class P(e.IntEnum)`, `x - x == 0` | 4770 | ok | PROVED | PROVED |
| control: alias-based member bound / `is` | 4771 | ok | PROVED | PROVED |
**Blast radius** (shared): root 2308 base / 2313 candidate .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref
2186/2186 0/0/0; mirror-emit-sweep 53/53 0/0/0 (`--min-files 50`) — no OWED proof.
**Gates** (one run for #352-#356, all rc 0): check-self-annotate-sync (926 verbatim), self-annotate-mirror-check (53), GATES_PLANES,
check-getattr-erasure (DECLARED 0), GATES_STDLIB, doc-coherency --check, check-assumed-facts (85 facts, all reviewed),
check-dropped-mutation (0 dropped; ratchets 0/51/5/0), check-refusal-witness-coverage (294 demonstrated, 5 undemonstrated =
ceiling 5), check-trusted-reasons (420/420, ratchet 259), check-trusted-raises-honesty (61 = ratchet),
check-assigns-underdeclaration --transitive (TRAP 3, HOLE 0).
**Residuals.** An enum built on an imported user enum WITHOUT a member-shaped body has no members to misuse; one with members is
handled conservatively, but its `C(v)` (#355) is not checked (only definite enums). Bases computed at runtime (`type(...)`,
`getattr`) are UNKNOWN, hence never transparent.
