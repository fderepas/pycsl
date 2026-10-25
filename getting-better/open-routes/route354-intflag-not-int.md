# OPEN ROUTE #354 — IntFlag IS TREATED AS int — `~`, STRICT-BOUNDARY `|` / `^` ARE MISLOWERED
**Status: REPAIRED, candidate (gen #37, 2026-10-25; opened the same day), Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r354/`: `e05_intflag_invert.py`, `e39_intflag_strict_or.py`, `e40_intflag_strict_ctor_int.py`.

`~x` on an IntFlag member is lowered `(-x)-1` (e05: `x + ~x == -1` proved; CPython 3, `~A == B`); `class F(IntFlag, boundary=STRICT)`: `x | 4` / `x ^ 8` under no_exception prove (CPython ValueError).

Repair: Take IntFlag (and Flag) out of the int-like set, or refuse `~ | & ^` on their members; any class keyword (`boundary=`) makes the enum opaque.

## REPAIR (2026-10-25, r352 executor off 1a9cfa42; code 46558356, corpus + census 0855e796, docs 9a2cbb48 (annotations §7.30 / translational §T.6.41), route docs)
**Design (shared by #352-#356): one rewrite of route #339's classifier inside the same inline `_run_pipeline` block, plus two
checks after its context walk; sound refusals only (`PYCSL-SEM-ENUM-MEMBER-OPERATION`, no new code), no emission change, no new
def (mirror twin `\trusted`), ledger 3.** CENSUS before landing (CPython `ast`, every plane): enum-bearing files are the #339
corpus witnesses 4590-4601, 4243 (`Color.RED.value`), the mirror's `pure_ast._Precedence(_enum.IntEnum)` via `import enum as
_enum` (resolved now: still transparent, its 52 uses are members), pyref `stdlib/enum/*` (no enum class), pycsl_lib 0; no
`IntFlag` / `Flag` / mixin / `__members__` / `C(v)` user anywhere; classes with an unclassifiable (non-stdlib) imported base:
18, of which 0 have a member-shaped body (1344's `m = lambda` is a method, excluded) — so the possibly-enum rule moves nothing.
RULE (#354): `IntFlag` and `Flag` leave the int-like set (also `class F(int, Flag)`, a NEW latent: its `int` base made it int-like);
their members are OPAQUE (no `~ | & ^`, no arithmetic). A class keyword anywhere in the MRO (`boundary=`, `metaclass=`) makes the
enum opaque.
**Probe table** (full pycsl proof via heavy.sh; base = 1a9cfa42 worktree; witnesses under `witnesses-r354/`):
| witness | corpus | CPython | base (1a9cfa42) | after |
|---|---|---|---|---|
| e05 IntFlag `x + ~x == -1` | 4757 | violates | PROVED | REFUSED |
| e39 `IntFlag, boundary=STRICT`: `x | 4` under `no_exception \all` | 4758 | ValueError | PROVED | REFUSED |
| e40 `IntFlag, boundary=STRICT`: `x ^ 8` | 4759 | ValueError | PROVED | REFUSED |
| NEW latent: `class F(int, Flag)`, `x + ~x == -1` | 4760 | violates | PROVED | REFUSED |
| control: IntFlag member bound / `is` | 4773 | ok | PROVED | PROVED |
**Blast radius** (shared): root 2308 base / 2313 candidate .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref
2186/2186 0/0/0; mirror-emit-sweep 53/53 0/0/0 (`--min-files 50`) — no OWED proof.
**Gates** (one run for #352-#356, all rc 0): check-self-annotate-sync (926 verbatim), self-annotate-mirror-check (53), GATES_PLANES,
check-getattr-erasure (DECLARED 0), GATES_STDLIB, doc-coherency --check, check-assumed-facts (85 facts, all reviewed),
check-dropped-mutation (0 dropped; ratchets 0/51/5/0), check-refusal-witness-coverage (294 demonstrated, 5 undemonstrated =
ceiling 5), check-trusted-reasons (420/420, ratchet 259), check-trusted-raises-honesty (61 = ratchet),
check-assigns-underdeclaration --transitive (TRAP 3, HOLE 0).
**Residuals.** Over-refusal: IntFlag arithmetic that IS int's (`x + 1`) is refused (0 users measured). A faithful flag model
(per-boundary `~ | & ^`) is not attempted.
