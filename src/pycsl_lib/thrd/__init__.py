# Pure model for threading — thread primitives
# Models Lock and Thread as state machines.

""" # pycsl"""


#@ class invariant self._locked >= 0
#@ class invariant self._locked <= 1
class Lock:
    """Abstract lock (acquired/released state)."""

    #@ ensures self._locked == 0
    def __init__(self) -> None:
        self._locked: int = 0

    #@ requires self._locked == 0
    #@ ensures self._locked == 1
    #@ assigns self._locked
    def acquire(self) -> None:
        """Acquire the lock."""
        self._locked = 1

    #@ requires self._locked == 1
    #@ ensures self._locked == 0
    #@ assigns self._locked
    def release(self) -> None:
        """Release the lock."""
        self._locked = 0

    #@ ensures \result == self._locked
    def locked(self) -> int:
        """Return 1 if locked, 0 if free."""
        return self._locked


""" # pycsl"""


#@ class invariant self._alive >= 0
#@ class invariant self._alive <= 1
class Thread:
    """Abstract thread (alive/dead state)."""

    #@ ensures self._alive == 0
    #@ ensures self._daemon == 0
    def __init__(self) -> None:
        self._alive: int = 0
        self._daemon: int = 0

    #@ requires self._alive == 0
    #@ ensures self._alive == 1
    #@ assigns self._alive
    def start(self) -> None:
        """Start thread execution."""
        self._alive = 1

    #@ requires self._alive == 1
    #@ ensures self._alive == 0
    #@ assigns self._alive
    def join(self) -> None:
        """Wait for thread to finish."""
        self._alive = 0

    #@ ensures \result == self._alive
    def is_alive(self) -> int:
        """Return 1 if running, 0 if not."""
        return self._alive


#@ ensures \result >= 1
def active_count() -> int:
    """Return number of active threads (at least main)."""
    return 1


#@ ensures \result >= 0
def current_thread() -> int:
    """Return current thread identifier."""
    return 0
