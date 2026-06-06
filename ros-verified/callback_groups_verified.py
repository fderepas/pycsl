"""Phase 2 — Callback group mutual exclusion (rclpy cyber-threat #2).

Verifies the data invariant of MutuallyExclusiveCallbackGroup:
  * the active flag is always 0 or 1 (class invariant)
  * beginning_execution grants access only when idle (active == 0)
  * ending_execution restores idle state (requires active == 1)
  * mutual exclusion: two consecutive beginning_execution calls cannot
    both return 1

Models the Lock-protected section as sequential code; assumes Lock
provides the atomicity guarantees.

Maps to ros-report.md Threat #2 — executor starvation / deadlock.
Source: rclpy/rclpy/rclpy/callback_groups.py
"""
""  # pycsl

#@ class invariant self._active == 0 or self._active == 1
class MutexGroup:
    def __init__(self):
        self._active = 0

    #@ ensures (\old(self._active) == 0) ==> (\result == 1)
    #@ ensures (\old(self._active) == 1) ==> (\result == 0)
    #@ assigns \nothing
    def can_execute(self) -> int:
        if self._active == 0:
            return 1
        return 0

    #@ ensures (\old(self._active) == 0) ==> (self._active == 1 and \result == 1)
    #@ ensures (\old(self._active) == 1) ==> (self._active == 1 and \result == 0)
    #@ assigns self._active
    def beginning_execution(self) -> int:
        if self._active == 0:
            self._active = 1
            return 1
        return 0

    #@ requires self._active == 1
    #@ ensures self._active == 0
    #@ assigns self._active
    def ending_execution(self) -> None:
        self._active = 0


if __name__ == "__main__":
    g = MutexGroup()
    assert g.can_execute() == 1

    assert g.beginning_execution() == 1
    assert g.can_execute() == 0
    assert g.beginning_execution() == 0

    g.ending_execution()
    assert g.can_execute() == 1

    print("PASS callback_groups_verified")
