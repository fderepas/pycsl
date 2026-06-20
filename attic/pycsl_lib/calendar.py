"""PyCSL mock for Python's calendar module — Functions for working with calendars, including some emulation."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/calendar.py
#@ requires True
#@ ensures True
def setfirstweekday(weekday: int) -> int:
    """Mock: Sets the weekday (``0`` is Monday, ``6`` is Sunday) to start each week. The values :const:`MONDAY`, :const:`TUESDAY`, :c..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/calendar.py
#@ requires True
#@ ensures True
def firstweekday() -> int:
    """Mock: Returns the current setting for the weekday to start each week."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.isleap
#@ ensures \result == 0 or \result == 1
#@ ensures year % 4 != 0 ==> \result == 0
#@ ensures year % 400 == 0 ==> \result == 1
#@ ensures year % 100 == 0 and year % 400 != 0 ==> \result == 0
#@ ensures year % 4 == 0 and year % 100 != 0 ==> \result == 1
def isleap(year: int) -> int:
    """Mock: Returns :const:`True` if *year* is a leap year, otherwise :const:`False`."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.leapdays
#@ requires y1 <= y2
#@ ensures \result >= 0
#@ ensures \result <= y2 - y1
def leapdays(y1: int, y2: int) -> int:
    """Mock: Returns the number of leap years in the range from *y1* to *y2* (exclusive), where *y1* and *y2* are years. This functio..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.weekday
#@ requires 1 <= month <= 12
#@ requires 1 <= day <= 31
#@ ensures 0 <= \result <= 6
def weekday(year: int, month: int, day: int) -> int:
    """Mock: Returns the day of the week (``0`` is Monday) for *year* (``1970``--...), *month* (``1``--``12``), *day* (``1``--``31``)..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.weekheader
#@ requires n >= 1
#@ ensures \result != ""
def weekheader(n: int) -> int:
    """Mock: Return a header containing abbreviated weekday names. *n* specifies the width in characters for one weekday."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.monthrange
#@ requires year >= 1
#@ requires 1 <= month <= 12
#@ ensures 0 <= \result <= 6
def monthrange(year: int, month: int) -> int:
    """Mock: Returns weekday of first day of the month and number of days in month, for the specified *year* and *month*."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.monthcalendar
#@ requires year >= 1
#@ requires month >= 1
#@ requires month <= 12
#@ ensures True
def monthcalendar(year: int, month: int) -> int:
    """Mock: Returns a matrix representing a month's calendar.  Each row represents a week; days outside of the month are represented..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.prmonth
#@ requires 1 <= themonth <= 12
#@ requires w >= 0
#@ requires l >= 0
#@ ensures True
def prmonth(theyear: int, themonth: int, w: int, l: int) -> int:
    """Mock: Prints a month's calendar as returned by :func:`month`."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.month
#@ requires theyear >= 1
#@ requires themonth >= 1
#@ requires themonth <= 12
#@ requires w >= 0
#@ requires l >= 0
#@ ensures True
def month(theyear: int, themonth: int, w: int, l: int) -> int:
    """Mock: Returns a month's calendar in a multi-line string using the :meth:`~TextCalendar.formatmonth` of the :class:`TextCalenda..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.prcal
#@ ensures True
#@ assigns \nothing
def prcal(year: int, w: int, l: int, c: int, m: int) -> int:
    """Mock: Prints the calendar for an entire year as returned by  :func:`calendar`."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.calendar
#@ ensures \result >= 0
def calendar(year: int, w: int, l: int, c: int, m: int) -> int:
    """Mock: Returns a 3-column calendar for an entire year as a multi-line string using the :meth:`~TextCalendar.formatyear` of the ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/calendar.html#calendar.timegm
# cite:_note: return value is a Unix timestamp (seconds since 1970-01-01 00:00:00 UTC); negative for pre-epoch dates; exact value requires calendar arithmetic not expressible in this contract language
#@ ensures True
def timegm(tuple: int) -> int:
    """Mock: An unrelated but handy function that takes a time tuple such as returned by the :func:`~time.gmtime` function in the :mo..."""
    return 0
