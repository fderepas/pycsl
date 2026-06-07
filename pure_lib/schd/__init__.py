# Pure model for sched — event scheduler
# Models scheduler as event-count tracker.

""" # pycsl"""


#@ class invariant self._events >= 0
class Scheduler:
    """Abstract event scheduler tracking pending event count."""

    #@ ensures self._events == 0
    def __init__(self) -> None:
        self._events: int = 0

    #@ ensures self._events == \old(self._events) + 1
    #@ assigns self._events
    def enter(self, delay: int, priority: int) -> None:
        """Schedule event after delay with priority."""
        self._events = self._events + 1

    #@ ensures self._events == \old(self._events) + 1
    #@ assigns self._events
    def enterabs(self, time: int, priority: int) -> None:
        """Schedule event at absolute time with priority."""
        self._events = self._events + 1

    #@ requires self._events > 0
    #@ ensures self._events == \old(self._events) - 1
    #@ assigns self._events
    def cancel(self, event_id: int) -> None:
        """Cancel a scheduled event."""
        self._events = self._events - 1

    #@ ensures \result == self._events
    def queue_size(self) -> int:
        """Return number of pending events."""
        return self._events

    #@ ensures \result >= 0
    #@ ensures \result <= 1
    def empty(self) -> int:
        """Return 1 if queue empty, else 0."""
        if self._events == 0:
            return 1
        return 0

    #@ ensures self._events == 0
    #@ assigns self._events
    def run(self) -> None:
        """Run all scheduled events (drains queue)."""
        self._events = 0
