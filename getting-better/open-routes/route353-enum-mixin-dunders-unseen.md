# OPEN ROUTE #353 — DUNDERS SUPPLIED BY A NON-ENUM MIXIN ARE NOT SEEN BY THE #339 CLASSIFIER
**Status: REPAIRED, candidate (gen #37, 2026-10-25; opened the same day), Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r353/`: `e03_mixin_sub_intenum.py`, `e04_mixin_eq_enum.py`, `e26_mixin_hash_raise.py`, `e27_intenum_via_int_mixin_class.py`, `e29_mixin_lt_enum_base_chain.py`.

Dunders are collected from the class body and the file's enum bases only. A mixin `M` before IntEnum / int supplying `__sub__` / `__lt__` / `__eq__` leaves the enum 'transparent' (e03, e27, e29: `x - x == 0`, `x < x` False proved; CPython 1 / True), or `==` / `hash` admitted on an opaque enum (e04 `x == x` True vs False; e26 `__eq__` without `__hash__` => hash TypeError).

Repair: Compute dunders over the whole C3 linearisation (reuse #344's MRO code); an enum is int-like only if every class before `int` in its MRO is a stdlib enum class or `int`; an `__eq__` without `__hash__` anywhere in the MRO means `__hash__ = None`.

## REPAIR (2026-10-25, r352 executor off 1a9cfa42; code 46558356, corpus + census 0855e796, docs 9a2cbb48 (annotations §7.30 / translational §T.6.41), route docs)
**Design (shared by #352-#356): one rewrite of route #339's classifier inside the same inline `_run_pipeline` block, plus two
checks after its context walk; sound refusals only (`PYCSL-SEM-ENUM-MEMBER-OPERATION`, no new code), no emission change, no new
def (mirror twin `\trusted`), ledger 3.** CENSUS before landing (CPython `ast`, every plane): enum-bearing files are the #339
corpus witnesses 4590-4601, 4243 (`Color.RED.value`), the mirror's `pure_ast._Precedence(_enum.IntEnum)` via `import enum as
_enum` (resolved now: still transparent, its 52 uses are members), pyref `stdlib/enum/*` (no enum class), pycsl_lib 0; no
`IntFlag` / `Flag` / mixin / `__members__` / `C(v)` user anywhere; classes with an unclassifiable (non-stdlib) imported base:
18, of which 0 have a member-shaped body (1344's `m = lambda` is a method, excluded) — so the possibly-enum rule moves nothing.
RULE (#353): an enum's dunders are the union over EVERY file class of its MRO (the C3 linearisation holds exactly the transitive
base closure; any dunder there is treated as overriding, an over-approximation of which one wins, so route #344's ordering code
is not needed); it is int-like only if its MRO holds nothing but `IntEnum` / `int` / `Enum` / `ReprEnum` / `object` and file ENUM
classes (any non-enum file mixin, even dunder-free, a stdlib / unknown base, makes it OPAQUE). `hash(x)` is admitted only when
neither `__hash__` nor `__eq__` is in the MRO's dunders (`__eq__` without `__hash__` sets `__hash__ = None`).
**Probe table** (full pycsl proof via heavy.sh; base = 1a9cfa42 worktree; witnesses under `witnesses-r353/`):
| witness | corpus | CPython | base (1a9cfa42) | after |
|---|---|---|---|---|
| e03 `class C(M, IntEnum)`, `M.__sub__`, `x - x == 0` | 4752 | violates | PROVED | REFUSED |
| e04 `class C(M, Enum)`, `M.__eq__`, `x == x` | 4753 | violates | PROVED | REFUSED |
| e26 mixin `__eq__` w/o `__hash__`, `hash(x)` under `no_exception \all` | 4754 | TypeError | PROVED | REFUSED |
| e27 `class C(M, int, Enum)`, `M.__sub__` | 4755 | violates | PROVED | REFUSED |
| e29 `class C(M, Base)`, `Base(IntEnum)`, `M.__lt__` | 4756 | violates | PROVED | REFUSED |
| control: `class C(int, Enum)`, `x - x == 0` | 4772 | ok | PROVED | PROVED |
**Blast radius** (shared): root 2308 base / 2313 candidate .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref
2186/2186 0/0/0; mirror-emit-sweep 53/53 0/0/0 (`--min-files 50`) — no OWED proof.
**Gates** (one run for #352-#356, all rc 0): check-self-annotate-sync (926 verbatim), self-annotate-mirror-check (53), GATES_PLANES,
check-getattr-erasure (DECLARED 0), GATES_STDLIB, doc-coherency --check, check-assumed-facts (85 facts, all reviewed),
check-dropped-mutation (0 dropped; ratchets 0/51/5/0), check-refusal-witness-coverage (294 demonstrated, 5 undemonstrated =
ceiling 5), check-trusted-reasons (420/420, ratchet 259), check-trusted-raises-honesty (61 = ratchet),
check-assigns-underdeclaration --transitive (TRAP 3, HOLE 0).
**Residuals.** Over-refusal: a dunder-free non-enum mixin, or a dunder later in the MRO than `int` (where int's wins), makes the
enum opaque (0 users measured). Mixins imported from another module are UNKNOWN (opaque), not inspected.
