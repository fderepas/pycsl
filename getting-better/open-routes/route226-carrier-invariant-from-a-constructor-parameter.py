"""ROUTE #226 CARRIER (second shape) — the invariant is established by NOBODY, and the
field comes from an `__init__` PARAMETER.

This file PROVES A FALSE CONTRACT TODAY, which is why it lives here and not in the corpus:
`# pycsl-expected: FAIL` would be an XPASS (a red suite) and `PASS` would write "this false
proof is expected" into the reference set. `bin/check-open-route-carriers.py` runs it and
asserts the verdict this route's record states.

THE FIRST CARRIER (`route226-carrier-constructor-never-establishes-the-invariant.py`) is
CLOSED: the constructor obligation is now emitted for a paramless `__init__` that stores int
literals, so that file no longer verifies. THIS shape is what increment 1 deliberately did
not close. `self.n = n` has no literal for the obligation to be stated about, so nothing is
emitted and the invariant is still free.

    #@ class invariant self.n >= 5
    class C:
        def __init__(self, n: int) -> None: self.n = n
        #@ ensures \\result >= 5
        def get(self) -> int: return self.n

CLOSED by increment 2. This carrier verified until the obligation learned to
quantify over the PARAMETER instead of substituting a literal; it now FAILS. Kept
because a closed carrier is the cheapest regression test a route has.

THE ROUTE IS NOT CLOSED. The COMPUTED-store shape still carries it and is the
registered carrier: `route226-carrier-computed-constructor-store.py`.

WAS: SUCCESS. CPython: `C(1).get()` is 1, and `1 >= 5` is False.

The measured surround, so increment 2 is not designed blind:
  · add `c = C(1)` to the file                          FAILED  (construction site checked)
  · add `#@ requires n >= 5` to `__init__` and `C(7)`   SUCCESS (the precondition works)
so the honest statement for this shape is `forall n. n >= 5`, which is false — such a class
should not verify unless `__init__` carries a `#@ requires`.

WHEN THIS STOPS PROVING, the route is probably closed and
`route226-a-class-invariant-the-constructor-never-establishes.md` must be updated in the
SAME commit — that is the whole point of the carrier gate.
"""
_ = 0  # anchor


#@ class invariant self.n >= 5
class C:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n
