"""Test 0402 — UB-7.5: `__del__` with `#@ allow_finalizer` is accepted."""
""  # pycsl
#@ class invariant self._n >= 0
#@ allow_finalizer
class WithFinalizer:
    def __init__(self) -> None:
        self._n: int = 0

    #@ assigns self._n
    def __del__(self) -> None:
        # explicit acknowledgment via allow_finalizer
        #
        # (#49) gen #31 — THE `#@ assigns` IS NEW, AND IT IS THE FIRST TIME THIS BODY IS
        # CHECKED AT ALL. Dunders used to be dropped before any IR was built, so `__del__`
        # was invisible: `#@ allow_finalizer` meant "we ignore your finalizer". With dunders
        # emitted the body is lowered and its frame is a goal, and a `self._n = 0` under an
        # ABSENT `#@ assigns` (which the emitter reads as `assigns \nothing`) does not hold.
        # Declaring the write is not a weakening of what this file tests — it is what makes
        # the test real. Corpus 1826 is the twin that proves the check now bites: the same
        # finalizer setting `self._n = -1` PROVED before (nothing looked) and FAILS now on
        # the class invariant.
        #
        # THE PERIMETER IS UNCHANGED IN WHAT IT DOES NOT PROMISE: `allow_finalizer`'s stated
        # hazard is finalizer TIMING, which is non-deterministic in CPython, and emitting the
        # body models none of it — no call site invokes `withfinalizer____del__`. What the
        # build adds is a body check, not a timing model.
        self._n = 0


if __name__ == "__main__":
    pass
