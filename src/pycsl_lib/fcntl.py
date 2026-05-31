"""PyCSL mock for Python's fcntl module — The fcntl() and ioctl() system calls."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def fcntl(fd: int, cmd: int, arg: int) -> int:
    """Mock: Perform the operation *cmd* on file descriptor *fd* (file objects providing a :meth:`~io.IOBase.fileno` method are accep..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ioctl(fd: int, request: int, arg: int, mutate_flag: int) -> int:
    """Mock: This function is identical to the :func:`~fcntl.fcntl` function, except that the argument handling is even more complica..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def flock(fd: int, operation: int) -> int:
    """Mock: Perform the lock operation *operation* on file descriptor *fd* (file objects providing a :meth:`~io.IOBase.fileno` metho..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lockf(fd: int, cmd: int, len: int, start: int, whence: int) -> int:
    """Mock: This is essentially a wrapper around the :func:`~fcntl.fcntl` locking calls. *fd* is the file descriptor (file objects p..."""
    return 0
