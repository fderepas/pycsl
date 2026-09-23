r"""Test 1815 — ROUTE #218 WITNESS (expected FAIL): an explicitly-called DUNDER that
writes self state is no longer modelled as PURE.

THE DEFECT. `Module5._should_skip_method` drops EVERY dunder before any IR is built, so
Module 6 knows nothing about `__enter__` at all. An explicit `c.__enter__()` therefore
minted an abstract

    val c___enter___0 (self: c) : int

with NO `writes` — and Why3 reads a `val` with no `writes` as PURE. This exact file
PROVED `\result == 0` while CPython answers **-7**, and the TRUE twin (`== -7`) FAILED:
a false contract proving while the true one is rejected, the route standard met exactly.

`PYCSL-CONTRADICTORY-ASSIGNS` describes this hazard in its own message ("a `val` with no
`writes` — which Why3 reads as PURE") and could not fire here: its population is stubs
whose clauses CONFLICT, and this stub's clauses never reached the emitter at all.

THE `#@ assigns` CLAUSE IS NOT THE TRIGGER. Measured: deleting this dunder's annotations
leaves the false proof standing. A BODY that writes self state is enough — which is why
the repair keys on the dropped body (`Module5._record_skipped_dunder_writes`) and not on
a clause. ZERO dunders anywhere in the five populations declare `#@ assigns self.`.

THE REPAIR IS THE HONEST-MODEL ONE, NOT THE FULL ONE. The minted `val` now carries
`writes { self.v }`, so the caller proves NOTHING about `v` across the call instead of
proving it UNCHANGED: a FALSE claim became an ABSENT one. Both `\result == 0` (this file)
and `\result == -7` (the true twin) now FAIL. Emitting dunders as ordinary methods — what
witness 1800 and route #216 wait on — is the larger build that would make the true twin
PROVE.

CONTROLS: 1816 (a READ-ONLY dunder still verifies — the repair is not a ban on dunder
calls) and 1817 (the NON-dunder spelling, which always failed correctly and pins the
defect to the skip rather than to the contract).
"""
# pycsl-expected: FAIL


#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    #@ ensures self.v == 7
    def __enter__(self) -> int:
        self.v = 7
        return 0


#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _r: int = c.__enter__()
    after: int = c.v
    return before - after
