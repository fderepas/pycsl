"""PyCSL mock for Python's time module — Time access and conversions."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def asctime(t: int) -> int:
    """Mock: Convert a tuple or :class:`struct_time` representing a time as returned by :func:`gmtime` or :func:`localtime` to a stri..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pthread_getcpuclockid(thread_id: int) -> int:
    """Mock: Return the *clk_id* of the thread-specific CPU-time clock for the specified *thread_id*. Use :func:`threading.get_ident`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def clock_getres(clk_id: int) -> int:
    """Mock: Return the resolution (precision) of the specified clock *clk_id*.  Refer to :ref:`time-clock-id-constants` for a list o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def clock_gettime(clk_id_____float: int) -> int:
    """Mock: Return the time of the specified clock *clk_id*.  Refer to :ref:`time-clock-id-constants` for a list of accepted values ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def clock_gettime_ns(clk_id_____int: int) -> int:
    """Mock: Similar to :func:`clock_gettime` but return time as nanoseconds. .. availability:: Unix. .. versionadded:: 3.7"""
    return 0

#@ \trusted
#@ ensures \result == 0
def clock_settime(clk_id: int, time: int) -> int:
    """Mock: Set the time of the specified clock *clk_id*.  Currently, :data:`CLOCK_REALTIME` is the only accepted value for *clk_id*..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def clock_settime_ns(clk_id: int, time: int) -> int:
    """Mock: Similar to :func:`clock_settime` but set time with nanoseconds. .. availability:: Unix, not Android, not iOS. .. version..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ctime(secs: int) -> int:
    """Mock: Convert a time expressed in seconds since the epoch_ to a string of a form: ``'Sun Jun 20 23:21:05 1993'`` representing ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_clock_info(name: int) -> int:
    """Mock: Get information on the specified clock as a namespace object. Supported clock names and the corresponding functions to r..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def gmtime(secs: int) -> int:
    """Mock: Convert a time expressed in seconds since the epoch_ to a :class:`struct_time` in UTC in which the dst flag is always ze..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def localtime(secs: int) -> int:
    """Mock: Like :func:`gmtime` but converts to local time.  If *secs* is not provided or :const:`None`, the current time as returne..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mktime(t: int) -> int:
    """Mock: This is the inverse function of :func:`localtime`.  Its argument is the :class:`struct_time` or full 9-tuple (since the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def monotonic(_____float: int) -> int:
    """Mock: Return the value (in fractional seconds) of a monotonic clock, i.e. a clock that cannot go backwards.  The clock is not ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def monotonic_ns(_____int: int) -> int:
    """Mock: Similar to :func:`monotonic`, but return time as nanoseconds. .. versionadded:: 3.7"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def perf_counter(_____float: int) -> int:
    """Mock: .. index:: single: benchmarking Return the value (in fractional seconds) of a performance counter, i.e. a clock with the..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def perf_counter_ns(_____int: int) -> int:
    """Mock: Similar to :func:`perf_counter`, but return time as nanoseconds. .. versionadded:: 3.7"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def process_time(_____float: int) -> int:
    """Mock: .. index:: single: CPU time single: processor time single: benchmarking Return the value (in fractional seconds) of the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def process_time_ns(_____int: int) -> int:
    """Mock: Similar to :func:`process_time` but return time as nanoseconds. .. versionadded:: 3.7"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sleep(secs: int) -> int:
    """Mock: Suspend execution of the calling thread for the given number of seconds. The argument may be a non-integer to indicate a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def strftime(format: int, t: int) -> int:
    """Mock: Convert a tuple or :class:`struct_time` representing a time as returned by :func:`gmtime` or :func:`localtime` to a stri..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def strptime(string: int, format: int) -> int:
    """Mock: Parse a string representing a time according to a format.  The return value is a :class:`struct_time` as returned by :fu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def time(_____float: int) -> int:
    """Mock: Return the time in seconds since the epoch_ as a floating-point number. The handling of `leap seconds`_ is platform depe..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def time_ns(_____int: int) -> int:
    """Mock: Similar to :func:`~time.time` but returns time as an integer number of nanoseconds since the epoch_. .. versionadded:: 3..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def thread_time(_____float: int) -> int:
    """Mock: .. index:: single: CPU time single: processor time single: benchmarking Return the value (in fractional seconds) of the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def thread_time_ns(_____int: int) -> int:
    """Mock: Similar to :func:`thread_time` but return time as nanoseconds. .. versionadded:: 3.7"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tzset() -> int:
    """Mock: Reset the time conversion rules used by the library routines. The environment variable :envvar:`TZ` specifies how this i..."""
    return 0
