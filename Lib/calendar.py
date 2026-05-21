"""PyCSL mock for Python's calendar module — Functions for working with calendars, including some emulation."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def setfirstweekday(weekday: int) -> int:
    """Mock: Sets the weekday (``0`` is Monday, ``6`` is Sunday) to start each week. The values :const:`MONDAY`, :const:`TUESDAY`, :c..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def firstweekday() -> int:
    """Mock: Returns the current setting for the weekday to start each week."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isleap(year: int) -> int:
    """Mock: Returns :const:`True` if *year* is a leap year, otherwise :const:`False`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def leapdays(y1: int, y2: int) -> int:
    """Mock: Returns the number of leap years in the range from *y1* to *y2* (exclusive), where *y1* and *y2* are years. This functio..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def weekday(year: int, month: int, day: int) -> int:
    """Mock: Returns the day of the week (``0`` is Monday) for *year* (``1970``--...), *month* (``1``--``12``), *day* (``1``--``31``)..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def weekheader(n: int) -> int:
    """Mock: Return a header containing abbreviated weekday names. *n* specifies the width in characters for one weekday."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def monthrange(year: int, month: int) -> int:
    """Mock: Returns weekday of first day of the month and number of days in month, for the specified *year* and *month*."""
    return 0

#@ \trusted
#@ ensures \result == 0
def monthcalendar(year: int, month: int) -> int:
    """Mock: Returns a matrix representing a month's calendar.  Each row represents a week; days outside of the month are represented..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prmonth(theyear: int, themonth: int, w: int, l: int) -> int:
    """Mock: Prints a month's calendar as returned by :func:`month`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def month(theyear: int, themonth: int, w: int, l: int) -> int:
    """Mock: Returns a month's calendar in a multi-line string using the :meth:`~TextCalendar.formatmonth` of the :class:`TextCalenda..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prcal(year: int, w: int, l: int, c: int, m: int) -> int:
    """Mock: Prints the calendar for an entire year as returned by  :func:`calendar`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def calendar(year: int, w: int, l: int, c: int, m: int) -> int:
    """Mock: Returns a 3-column calendar for an entire year as a multi-line string using the :meth:`~TextCalendar.formatyear` of the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def timegm(tuple: int) -> int:
    """Mock: An unrelated but handy function that takes a time tuple such as returned by the :func:`~time.gmtime` function in the :mo..."""
    return 0
