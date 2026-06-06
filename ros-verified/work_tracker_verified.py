"""Phase 3 — WorkTracker counter integrity (rclpy cyber-threat #2).

Verifies the _WorkTracker counter invariant:
  * _count is always >= 0 (class invariant)
  * enter_work increments by exactly 1
  * exit_work decrements by exactly 1 (requires _count >= 1)
  * is_idle correctly reports _count == 0

Models the Condition-protected section as sequential code; assumes
Condition provides the atomicity guarantees.

Maps to ros-report.md Threat #2 — executor starvation / deadlock.
Source: rclpy/rclpy/rclpy/executors.py lines 86-121
"""
""  # pycsl

#@ class invariant self._count >= 0
class WorkTracker:
    def __init__(self):
        self._count = 0

    #@ ensures self._count == \old(self._count) + 1
    #@ assigns self._count
    def enter_work(self) -> None:
        self._count = self._count + 1

    #@ requires self._count >= 1
    #@ ensures self._count == \old(self._count) - 1
    #@ assigns self._count
    def exit_work(self) -> None:
        self._count = self._count - 1

    #@ ensures (self._count == 0) ==> (\result == 1)
    #@ ensures (self._count != 0) ==> (\result == 0)
    #@ assigns \nothing
    def is_idle(self) -> int:
        if self._count == 0:
            return 1
        return 0


if __name__ == "__main__":
    w = WorkTracker()
    assert w.is_idle() == 1

    w.enter_work()
    assert w.is_idle() == 0

    w.enter_work()
    assert w.is_idle() == 0

    w.exit_work()
    assert w.is_idle() == 0

    w.exit_work()
    assert w.is_idle() == 1

    print("PASS work_tracker_verified")
