# Pure model for datetime — date and time
# Models as epoch-second based time tracking.

""" # pycsl"""


#@ class invariant self._timestamp >= 0
class DateTime:
    """Abstract datetime as Unix timestamp."""

    #@ requires year >= 1
    #@ requires month >= 1
    #@ requires month <= 12
    #@ requires day >= 1
    #@ requires day <= 31
    #@ ensures self._timestamp >= 0
    #@ ensures self._year == year
    #@ ensures self._month == month
    #@ ensures self._day == day
    def __init__(self, year: int, month: int, day: int) -> None:
        self._year: int = year
        self._month: int = month
        self._day: int = day
        self._timestamp: int = year * 365 + month * 30 + day

    #@ ensures \result == self._year
    def year(self) -> int:
        """Return year component."""
        return self._year

    #@ ensures \result == self._month
    def month(self) -> int:
        """Return month component."""
        return self._month

    #@ ensures \result == self._day
    def day(self) -> int:
        """Return day component."""
        return self._day

    #@ ensures \result == self._timestamp
    def timestamp(self) -> int:
        """Return Unix timestamp."""
        return self._timestamp


#@ ensures \result >= 0
def now() -> int:
    """Current time as timestamp."""
    return 0


#@ requires days >= 0
#@ ensures \result == days * 86400
def timedelta_seconds(days: int) -> int:
    """Convert timedelta days to total seconds."""
    return days * 86400


#@ requires ts >= 0
#@ ensures \result >= 0
def fromtimestamp(ts: int) -> int:
    """Create datetime from timestamp. Returns timestamp."""
    return ts
