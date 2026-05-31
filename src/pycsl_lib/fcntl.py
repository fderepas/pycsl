"""PyCSL mock for Python's fcntl module — The fcntl() and ioctl() system calls."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fcntl.html#fcntl.fcntl
#@ requires fd >= 0
#@ ensures True
def fcntl(fd: int, cmd: int, arg: int) -> int:
    """Mock: Perform the operation *cmd* on file descriptor *fd* (file objects providing a :meth:`~io.IOBase.fileno` method are accep..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fcntl.html#fcntl.ioctl
#@ requires fd >= 0
#@ ensures True
#@ assigns \nothing
def ioctl(fd: int, request: int, arg: int, mutate_flag: int) -> int:
    """Mock: This function is identical to the :func:`~fcntl.fcntl` function, except that the argument handling is even more complica..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fcntl.html#fcntl.flock
#@ requires fd >= 0
#@ requires operation >= 0
#@ ensures \result == 0
def flock(fd: int, operation: int) -> int:
    """Mock: Perform the lock operation *operation* on file descriptor *fd* (file objects providing a :meth:`~io.IOBase.fileno` metho..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fcntl.html#fcntl.lockf
#@ requires fd >= 0
#@ requires len >= 0
#@ requires whence == 0 or whence == 1 or whence == 2
#@ ensures True
def lockf(fd: int, cmd: int, len: int, start: int, whence: int) -> int:
    """Mock: This is essentially a wrapper around the :func:`~fcntl.fcntl` locking calls. *fd* is the file descriptor (file objects p..."""
    return 0
