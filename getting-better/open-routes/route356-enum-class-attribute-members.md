# OPEN ROUTE #356 — ENUM MEMBERS REACHED THROUGH CLASS-OBJECT ATTRIBUTES (`__members__`) KEEP INT LAWS
**Status: REPAIRED, candidate (gen #37, 2026-10-25; opened the same day), Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r356/`: `e20_members_values_loop.py`.

`for m in C.__members__.values(): m - m` under no_exception proves; CPython TypeError (plain Enum members).

Repair: Treat any load of a non-member attribute of an enum class (`__members__`, `_member_map_`, `_value2member_map_`, ...) as a member container and refuse it.

## REPAIR (2026-10-25, r352 executor off 1a9cfa42; code 46558356, corpus + census 0855e796, docs 9a2cbb48 (annotations §7.30 / translational §T.6.41), route docs)
**Design (shared by #352-#356): one rewrite of route #339's classifier inside the same inline `_run_pipeline` block, plus two
checks after its context walk; sound refusals only (`PYCSL-SEM-ENUM-MEMBER-OPERATION`, no new code), no emission change, no new
def (mirror twin `\trusted`), ledger 3.** CENSUS before landing (CPython `ast`, every plane): enum-bearing files are the #339
corpus witnesses 4590-4601, 4243 (`Color.RED.value`), the mirror's `pure_ast._Precedence(_enum.IntEnum)` via `import enum as
_enum` (resolved now: still transparent, its 52 uses are members), pyref `stdlib/enum/*` (no enum class), pycsl_lib 0; no
`IntFlag` / `Flag` / mixin / `__members__` / `C(v)` user anywhere; classes with an unclassifiable (non-stdlib) imported base:
18, of which 0 have a member-shaped body (1344's `m = lambda` is a method, excluded) — so the possibly-enum rule moves nothing.
RULE (#356): for every enum class `C`, a load `C.X` with `X` neither a member nor a name bound in the body of a file class of
`C`'s MRO (methods, class attributes) is REFUSED — `__members__`, `_member_map_`, `_value2member_map_`, `_member_names_`, `mro`,
... — and so is any store / delete through `C.X`.
**Probe table** (full pycsl proof via heavy.sh; base = 1a9cfa42 worktree; witnesses under `witnesses-r356/`):
| witness | corpus | CPython | base (1a9cfa42) | after |
|---|---|---|---|---|
| e20 `for m in C.__members__.values(): m - m` | 4765 | TypeError | PROVED | REFUSED |
| NEW shape: `for m in C._value2member_map_.values(): m - m` | 4766 | TypeError | PROVED | REFUSED |
| probe: `C.A = 5` under `no_exception \all` | — | AttributeError | REFUSED (name rebinding) | REFUSED |
**Blast radius** (shared): root 2308 base / 2313 candidate .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref
2186/2186 0/0/0; mirror-emit-sweep 53/53 0/0/0 (`--min-files 50`) — no OWED proof.
**Gates** (one run for #352-#356, all rc 0): check-self-annotate-sync (926 verbatim), self-annotate-mirror-check (53), run-soundness-planes (fast, 61/61 green),
check-getattr-erasure (DECLARED 0), check-stdlib-modules-verify (83 VERIFY; non-verifying set = the known 21), doc-coherency --check, check-assumed-facts (85 facts, all reviewed),
check-dropped-mutation (0 dropped; ratchets 0/51/5/0), check-refusal-witness-coverage (294 demonstrated, 5 undemonstrated =
ceiling 5), check-trusted-reasons (420/420, ratchet 259), check-trusted-raises-honesty (61 = ratchet),
check-assigns-underdeclaration --transitive (TRAP 3, HOLE 0).
**Residuals.** The class object reached otherwise (`type(x).__members__`, `x.__class__`, `getattr(C, ..)`, a class alias
`K = C`) is not tracked (route #339 residual (2)). Over-refusal: `C.__name__` / `C.__doc__` are refused (0 users).
