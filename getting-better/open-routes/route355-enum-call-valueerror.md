# OPEN ROUTE #355 — `C(v)` ON AN ENUM HAS NO ValueError OBLIGATION
**Status: REPAIRED, candidate (gen #37, 2026-10-25; opened the same day), Severity 1.** Red-team round 26 (2026-10-25, probes around the #339/#340/#343-#345 repairs); driver-reproduced on main 3d937bdb (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt26/driver-repro.txt`).
Witnesses `witnesses-r355/`: `e16_intenum_ctor_valueerror.py`, `e31_enum_ctor_valueerror_plain.py`.

`x = C(99)` under no_exception is emitted `let x = (any c)` and proves for IntEnum (e16) and plain Enum (e31); CPython ValueError. (`C["Z"]` already gets a goal and fails.)

Repair: Under no_exception, `C(v)` asserts `v` is one of the member values (or refuse it), as `C[k]` already does.

## REPAIR (2026-10-25, r352 executor off 1a9cfa42; code 46558356, corpus + census 0855e796, docs 9a2cbb48 (annotations §7.30 / translational §T.6.41), route docs)
**Design (shared by #352-#356): one rewrite of route #339's classifier inside the same inline `_run_pipeline` block, plus two
checks after its context walk; sound refusals only (`PYCSL-SEM-ENUM-MEMBER-OPERATION`, no new code), no emission change, no new
def (mirror twin `\trusted`), ledger 3.** CENSUS before landing (CPython `ast`, every plane): enum-bearing files are the #339
corpus witnesses 4590-4601, 4243 (`Color.RED.value`), the mirror's `pure_ast._Precedence(_enum.IntEnum)` via `import enum as
_enum` (resolved now: still transparent, its 52 uses are members), pyref `stdlib/enum/*` (no enum class), pycsl_lib 0; no
`IntFlag` / `Flag` / mixin / `__members__` / `C(v)` user anywhere; classes with an unclassifiable (non-stdlib) imported base:
18, of which 0 have a member-shaped body (1344's `m = lambda` is a method, excluded) — so the possibly-enum rule moves nothing.
RULE (#355): for EVERY enum of the file (transparent ones too), in every lowered function, `C(v)` is admitted only when its one
positional argument is a member `C.M`, or an `int` / `str` literal equal (same type) to a literal member value of `C`, with no
`__new__` in the MRO and the literal type the one CPython stores (`int` under an int mixin, `str` under a str mixin, either for a
plain Enum, never under another mixin / an unresolved base). Anything else is REFUSED regardless of the function's `no_exception`
(measured simpler: 0 `C(v)` users outside the witnesses; a faithful membership goal would need member values the opaque getter
does not carry).
**Probe table** (full pycsl proof via heavy.sh; base = 1a9cfa42 worktree; witnesses under `witnesses-r355/`):
| witness | corpus | CPython | base (1a9cfa42) | after |
|---|---|---|---|---|
| e16 IntEnum `C(99)` under `no_exception \all` | 4761 | ValueError | PROVED | REFUSED |
| e31 plain Enum `C(99)` | 4762 | ValueError | PROVED | REFUSED |
| NEW shape: `C(v)` with an `int` parameter | 4763 | ValueError | PROVED | REFUSED |
| NEW shape: `class C(str, Enum): A = "1"`, `C(1)` | 4764 | ValueError | PROVED | REFUSED |
| control: `C(1)`, `C("b")`, IntEnum `P(1)` | 4774 | ok | PROVED | PROVED |
**Blast radius** (shared): root 2308 base / 2313 candidate .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref
2186/2186 0/0/0; mirror-emit-sweep 53/53 0/0/0 (`--min-files 50`) — no OWED proof.
**Gates** (one run for #352-#356, all rc 0): check-self-annotate-sync (926 verbatim), self-annotate-mirror-check (53), GATES_PLANES,
check-getattr-erasure (DECLARED 0), GATES_STDLIB, doc-coherency --check, check-assumed-facts (85 facts, all reviewed),
check-dropped-mutation (0 dropped; ratchets 0/51/5/0), check-refusal-witness-coverage (294 demonstrated, 5 undemonstrated =
ceiling 5), check-trusted-reasons (420/420, ratchet 259), check-trusted-raises-honesty (61 = ratchet),
check-assigns-underdeclaration --transitive (TRAP 3, HOLE 0).
**Residuals.** Over-refusal: `C(v)` in a function with no `no_exception` claim, `Flag` composite values (`F(3)`), `auto()` members
(value not a literal) and `C(C.A)` (route #339 refuses the member as a call argument) are refused. `C(v)` of a possibly-enum class
(#352) is not checked.
