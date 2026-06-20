"""PyCSL mock for Python's select module — Wait for I/O completion on multiple streams."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def devpoll() -> int:
    """Mock: (Only supported on Solaris and derivatives.)  Returns a ``/dev/poll`` polling object; see section :ref:`devpoll-objects`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def epoll(sizehint: int, flags: int) -> int:
    """Mock: (Only supported on Linux 2.5.44 and newer.) Return an edge polling object, which can be used as Edge or Level Triggered ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def poll() -> int:
    """Mock: (Not supported by all operating systems.)  Returns a polling object, which supports registering and unregistering file d..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def kqueue() -> int:
    """Mock: (Only supported on BSD.)  Returns a kernel queue object; see section :ref:`kqueue-objects` below for the methods support..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def kevent(ident: int, filter: int, flags: int, fflags: int, data: int, udata: int) -> int:
    """Mock: (Only supported on BSD.)  Returns a kernel event object; see section :ref:`kevent-objects` below for the methods support..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def select(rlist: int, wlist: int, xlist: int, timeout: int) -> int:
    """Mock: This is a straightforward interface to the Unix :c:func:`!select` system call. The first three arguments are iterables o..."""
    return 0
