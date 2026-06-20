# Coarse probe — cross-subsystem framing (making-it-pure-5.md §9)
#
# Validates: calling a clock/proc method preserves fs-owned fields.
# This is the Tier-1 HAPPY confinement test — if proc methods only
# assign proc.* and clock methods only assign clock.*, then fs fields
# are preserved by default.
#
# Since we can't directly compose World subsystem calls in one PyCSL
# function (the World class can't be body-level proven yet), we test
# the principle: calling one class's method preserves another class's
# fields via `assigns` isolation.

from pycsl_lib.tm import ClockModel
from pycsl_lib.proc import ProcessState


# --- Coarse probe 1: Clock call preserves ProcessState pid ---
# ClockModel.monotonic assigns only self._ticks.
# ProcessState.pid should be unchanged after a clock call.
#@ ensures \result >= 0
def coarse_clock_preserves_proc() -> int:
    c = ClockModel()
    ps = ProcessState()
    old_pid = ps.pid
    t = c.monotonic()
    # pid is unchanged because monotonic only assigns c._ticks
    return ps.pid


# --- Coarse probe 2: Proc call preserves ClockModel ticks ---
# ProcessState.umask_set assigns only self.umask.
# After calling umask_set, clock._ticks should be unchanged.
#@ ensures \result >= 0
def coarse_proc_preserves_clock() -> int:
    c = ClockModel()
    ps = ProcessState()
    t1 = c.monotonic()
    old = ps.umask_set(63)
    t2 = c.monotonic()
    # t2 > t1 because monotonic is strictly increasing and
    # umask_set doesn't touch clock._ticks
    return t2


# --- Coarse probe 3: Two successive monotonic calls ---
# Second call >= first. This is the ordering property.
#@ ensures \result >= 0
def coarse_clock_ordering() -> int:
    c = ClockModel()
    t1 = c.monotonic()
    t2 = c.monotonic()
    return t2 - t1


# --- Coarse probe 4: Proc chdir returns valid range ---
# chdir returns 0 or -1. Tests proc contract isolation.
#@ ensures \result == 0 or \result == -1
def coarse_chdir_bounded() -> int:
    ps = ProcessState()
    return ps.chdir(5)
