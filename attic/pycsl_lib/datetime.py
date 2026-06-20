"""PyCSL mock for Python's datetime module.

Provides trusted stubs for date and time types.
Classes model object invariants; factory functions provide constructors.
"""
_ = 0  # anchor

# ── timedelta ───────────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._total_seconds >= 0
class timedelta:
    def __init__(self):
        self._total_seconds = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._total_seconds
    #@ assigns \nothing
    def total_seconds(self) -> int:
        return self._total_seconds

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.timedelta
#@ requires True
#@ ensures -999999999 <= \result <= 999999999
#@ assigns \nothing
    def days(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def seconds(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.timedelta.microseconds
#@ ensures \result >= 0
#@ ensures \result < 1000000
#@ assigns \nothing
    def microseconds(self) -> int:
        return 0

# ── date ────────────────────────────────────────────────────────────

#@ class invariant self._year >= 1 and self._year <= 9999
#@ class invariant self._month >= 1 and self._month <= 12
#@ class invariant self._day >= 1 and self._day <= 31
class date:
    def __init__(self):
        self._year = 1
        self._month = 1
        self._day = 1

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._year
    #@ assigns \nothing
    def year(self) -> int:
        return self._year

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._month
    #@ assigns \nothing
    def month(self) -> int:
        return self._month

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._day
    #@ assigns \nothing
    def day(self) -> int:
        return self._day

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0 and \result <= 6
    #@ assigns \nothing
    def weekday(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.date.toordinal
#@ requires True
#@ ensures \result >= 1
#@ assigns \nothing
    def toordinal(self) -> int:
        return 1

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.date.timetuple
#@ requires True
#@ ensures True
#@ assigns \nothing
    def timetuple(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def isoformat(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.strftime
#@ requires True
#@ ensures True
#@ assigns \nothing
    def strftime(self, fmt: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.date.replace
#@ requires True
#@ ensures True
#@ assigns \nothing
    def replace(self, year: int, month: int, day: int) -> int:
        return 0

# ── time ────────────────────────────────────────────────────────────

#@ class invariant self._hour >= 0 and self._hour <= 23
#@ class invariant self._minute >= 0 and self._minute <= 59
#@ class invariant self._second >= 0 and self._second <= 59
#@ class invariant self._microsecond >= 0 and self._microsecond <= 999999
class TimeObj:
    def __init__(self):
        self._hour = 0
        self._minute = 0
        self._second = 0
        self._microsecond = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._hour
    #@ assigns \nothing
    def hour(self) -> int:
        return self._hour

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._minute
    #@ assigns \nothing
    def minute(self) -> int:
        return self._minute

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._second
    #@ assigns \nothing
    def second(self) -> int:
        return self._second

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._microsecond
    #@ assigns \nothing
    def microsecond(self) -> int:
        return self._microsecond

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
    def isoformat(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.strftime
#@ requires True
#@ ensures True
#@ assigns \nothing
    def strftime(self, fmt: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.time.replace
#@ requires True
#@ ensures True
#@ assigns \nothing
    def replace(self, hour: int, minute: int, second: int, microsecond: int) -> int:
        return 0

# ── DatetimeObj ─────────────────────────────────────────────────────

#@ class invariant self._dt_year >= 1 and self._dt_year <= 9999
#@ class invariant self._dt_month >= 1 and self._dt_month <= 12
#@ class invariant self._dt_day >= 1 and self._dt_day <= 31
#@ class invariant self._dt_hour >= 0 and self._dt_hour <= 23
#@ class invariant self._dt_minute >= 0 and self._dt_minute <= 59
#@ class invariant self._dt_second >= 0 and self._dt_second <= 59
#@ class invariant self._dt_microsecond >= 0 and self._dt_microsecond <= 999999
class DatetimeObj:
    def __init__(self):
        self._dt_year = 1
        self._dt_month = 1
        self._dt_day = 1
        self._dt_hour = 0
        self._dt_minute = 0
        self._dt_second = 0
        self._dt_microsecond = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._dt_year
    #@ assigns \nothing
    def year(self) -> int:
        return self._dt_year

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._dt_month
    #@ assigns \nothing
    def month(self) -> int:
        return self._dt_month

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._dt_day
    #@ assigns \nothing
    def day(self) -> int:
        return self._dt_day

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._dt_hour
    #@ assigns \nothing
    def hour(self) -> int:
        return self._dt_hour

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._dt_minute
    #@ assigns \nothing
    def minute(self) -> int:
        return self._dt_minute

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._dt_second
    #@ assigns \nothing
    def second(self) -> int:
        return self._dt_second

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._dt_microsecond
    #@ assigns \nothing
    def microsecond(self) -> int:
        return self._dt_microsecond

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
#@ requires True
#@ ensures True
#@ assigns \nothing
    def timestamp(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def date_part(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def time_part(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0 and \result <= 6
    #@ assigns \nothing
    def weekday(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def isoformat(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def strftime(self, fmt: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def replace(self, year: int, month: int, day: int, hour: int, minute: int, second: int, microsecond: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.now
#@ requires True
#@ ensures True
#@ assigns \nothing
    def now(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def utcnow(self) -> int:
        return 0

# ── timezone ────────────────────────────────────────────────────────

#@ class invariant self._offset >= -86400 and self._offset <= 86400
class timezone:
    def __init__(self):
        self._offset = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._offset
    #@ assigns \nothing
    def utcoffset(self) -> int:
        return self._offset

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.tzinfo.tzname
#@ requires True
#@ ensures True
#@ assigns \nothing
    def tzname(self) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
#@ assigns \nothing
    def dst(self) -> int:
        return 0

# ── Standalone factory functions ────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.timedelta
#@ requires True
#@ ensures True
def timedelta_ctor(days: int, seconds: int, microseconds: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.timedelta.min
#@ requires True
#@ ensures True
def timedelta_min() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def timedelta_max() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def timedelta_resolution() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.date
#@ requires year >= 1 and year <= 9999
#@ requires month >= 1 and month <= 12
#@ requires day >= 1 and day <= 31
#@ ensures True
def date_ctor(year: int, month: int, day: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def date_today() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.date.fromtimestamp
#@ requires True
#@ ensures True
def date_fromtimestamp(timestamp: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.date.fromordinal
#@ requires True
#@ ensures True
def date_fromordinal(ordinal: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat
#@ requires True
#@ ensures True
def date_fromisoformat(date_string: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def date_fromisocalendar(year: int, week: int, day: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def date_min() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.date.max
#@ requires True
#@ ensures True
def date_max() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def date_resolution() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.time
#@ requires hour >= 0 and hour <= 23
#@ requires minute >= 0 and minute <= 59
#@ requires second >= 0 and second <= 59
#@ requires microsecond >= 0 and microsecond <= 999999
#@ ensures \result >= 0
def time_ctor(hour: int, minute: int, second: int, microsecond: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.time.fromisoformat
#@ requires True
#@ ensures True
def time_fromisoformat(time_string: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def time_min() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def time_max() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def time_resolution() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime
#@ requires year >= 1 and year <= 9999
#@ requires month >= 1 and month <= 12
#@ requires day >= 1 and day <= 31
#@ requires hour >= 0 and hour <= 23
#@ requires minute >= 0 and minute <= 59
#@ requires second >= 0 and second <= 59
#@ requires microsecond >= 0 and microsecond <= 999999
#@ ensures True
def datetime_ctor(year: int, month: int, day: int, hour: int, minute: int, second: int, microsecond: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def datetime_today() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def datetime_now() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def datetime_utcnow() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.fromtimestamp
#@ requires True
#@ ensures True
def datetime_fromtimestamp(timestamp: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.utcfromtimestamp
#@ requires True
#@ ensures True
def datetime_utcfromtimestamp(timestamp: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def datetime_fromordinal(ordinal: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def datetime_combine(d: int, t: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat
#@ requires True
#@ ensures True
def datetime_fromisoformat(date_string: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def datetime_fromisocalendar(year: int, week: int, day: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.strptime
#@ requires True
#@ ensures True
def datetime_strptime(date_string: int, fmt: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def datetime_min() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def datetime_max() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/datetime.html#datetime.datetime.resolution
#@ requires True
#@ ensures True
def datetime_resolution() -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/datetime.py
#@ requires True
#@ ensures True
def timezone_ctor(offset: int) -> int:
    return 0

#@ \trusted reviewer: python-stdlib
# cite: cpython/Lib/datetime.py
#@ requires True
#@ ensures True
def timezone_utc() -> int:
    return 0
