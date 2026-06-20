# Pure model for logging — logging framework
# Models Logger as level + handler-count tracker.

""" # pycsl"""

# Log levels as constants
DEBUG: int = 10
INFO: int = 20
WARNING: int = 30
ERROR: int = 40
CRITICAL: int = 50


#@ class invariant self._level >= 0
#@ class invariant self._handlers >= 0
class Logger:
    """Abstract logger with level and handler count."""

    #@ requires level >= 0
    #@ ensures self._level == level
    #@ ensures self._handlers == 0
    #@ ensures self._messages == 0
    def __init__(self, level: int) -> None:
        self._level: int = level
        self._handlers: int = 0
        self._messages: int = 0

    #@ requires level >= 0
    #@ ensures self._level == level
    #@ assigns self._level
    def setLevel(self, level: int) -> None:
        """Set logging level."""
        self._level = level

    #@ ensures self._handlers == \old(self._handlers) + 1
    #@ assigns self._handlers
    def addHandler(self, handler: int) -> None:
        """Add a handler."""
        self._handlers = self._handlers + 1

    #@ requires self._handlers > 0
    #@ ensures self._handlers == \old(self._handlers) - 1
    #@ assigns self._handlers
    def removeHandler(self, handler: int) -> None:
        """Remove a handler."""
        self._handlers = self._handlers - 1

    #@ ensures \result == self._level
    def getEffectiveLevel(self) -> int:
        """Return effective level."""
        return self._level

    #@ ensures self._messages == \old(self._messages) + 1
    #@ assigns self._messages
    def log(self, level: int, msg: int) -> None:
        """Log a message."""
        self._messages = self._messages + 1


#@ requires level >= 0
#@ ensures \result >= 0
def getLogger(level: int) -> int:
    """Get a logger (modeled as returning level)."""
    return level


#@ requires level >= 0
#@ ensures \result >= 0
def basicConfig(level: int) -> int:
    """Configure root logger. Returns 0."""
    return 0
