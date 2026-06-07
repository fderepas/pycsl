# Pure model for selectors — I/O multiplexing
# Models as registered fd count.

""" # pycsl"""


#@ class invariant self._registered >= 0
class Selector:
    """Abstract I/O multiplexing selector."""

    #@ ensures self._registered == 0
    def __init__(self) -> None:
        self._registered: int = 0

    #@ ensures self._registered == \old(self._registered) + 1
    #@ assigns self._registered
    def register(self, fd: int, events: int) -> None:
        """Register fd for monitoring."""
        self._registered = self._registered + 1

    #@ requires self._registered > 0
    #@ ensures self._registered == \old(self._registered) - 1
    #@ assigns self._registered
    def unregister(self, fd: int) -> None:
        """Unregister fd."""
        self._registered = self._registered - 1

    #@ ensures \result >= 0
    #@ ensures \result <= self._registered
    def select(self, timeout: int) -> int:
        """Wait for events. Returns ready count."""
        return 0

    #@ ensures self._registered == 0
    #@ assigns self._registered
    def close(self) -> None:
        """Close selector, unregister all."""
        self._registered = 0

    #@ ensures \result == self._registered
    def get_map_size(self) -> int:
        """Return number of registered fds."""
        return self._registered


# Event constants
EVENT_READ: int = 1
EVENT_WRITE: int = 2
