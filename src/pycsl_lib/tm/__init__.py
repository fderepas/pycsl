# pycsl_lib/tm — pure-Python time model
# Named 'tm' to avoid stdlib name clash (see pycsl-stdlib-coverage skill)
#
# Models a monotonic clock as a non-decreasing integer counter.
# Unix skill §8.4: "CLOCK_MONOTONIC never goes backward."
# TCB: rate and wall-clock duration are unmodelled — only ordering.


#@ class invariant self._ticks >= 0
class ClockModel:
    def __init__(self):
        self._ticks = 0

    #@ ensures \result >= 0
    #@ ensures self._ticks >= \result
    def monotonic(self) -> int:
        self._ticks = self._ticks + 1
        return self._ticks


# Module-level singleton for simple usage
_clock = ClockModel()

# HAPPY: only monotonic() may write the clock's ticks field
#@ happy clock_ownership:
#@     protects _clock._ticks
#@     except monotonic


#@ ensures \result >= 0
def monotonic() -> int:
    return _clock.monotonic()
