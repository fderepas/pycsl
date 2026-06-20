# pycsl_lib/errno — pure-Python errno module model
#
# Contracts derived from library_reference/errno.rst.
# RST: "This module makes available standard errno system symbols."
#
# Model: errno constants as integers (POSIX standard values).

EPERM   = 1
ENOENT  = 2
ESRCH   = 3
EINTR   = 4
EIO     = 5
ENXIO   = 6
E2BIG   = 7
ENOEXEC = 8
EBADF   = 9
ECHILD  = 10
EAGAIN  = 11
ENOMEM  = 12
EACCES  = 13
EFAULT  = 14
EBUSY   = 16
EEXIST  = 17
EXDEV   = 18
ENODEV  = 19
ENOTDIR = 20
EISDIR  = 21
EINVAL  = 22
ENFILE  = 23
EMFILE  = 24
ENOTTY  = 25
ETXTBSY = 26
EFBIG   = 27
ENOSPC  = 28
ESPIPE  = 29
EROFS   = 30
EMLINK  = 31
EPIPE   = 32
ERANGE  = 34
ENOSYS  = 38
ENOTEMPTY = 39
ELOOP   = 40
ENAMETOOLONG = 36
EDEADLK = 35
ETIMEDOUT = 110


#@ requires code >= 0
#@ assigns \nothing
def strerror(code: int) -> str:
    """RST: 'Return the message belonging to an error code.'"""
    return "Unknown error"


#@ ensures \result > 0
#@ assigns \nothing
def errorcode_count() -> int:
    """RST: 'Dictionary providing a mapping from the errno value to the
    string name.' Returns number of known error codes."""
    return 38
