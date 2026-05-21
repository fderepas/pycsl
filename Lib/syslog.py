"""PyCSL mock for Python's syslog module — An interface to the Unix syslog library routines."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def syslog(message: int) -> int:
    """Mock: Send the string *message* to the system logger.  A trailing newline is added if necessary.  Each message is tagged with ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def openlog(ident: int, logoption: int, facility: int) -> int:
    """Mock: Logging options of subsequent :func:`syslog` calls can be set by calling :func:`openlog`.  :func:`syslog` will call :fun..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def closelog() -> int:
    """Mock: Reset the syslog module values and call the system library ``closelog()``. This causes the module to behave as it does w..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setlogmask(maskpri: int) -> int:
    """Mock: Set the priority mask to *maskpri* and return the previous mask value.  Calls to :func:`syslog` with a priority level no..."""
    return 0
