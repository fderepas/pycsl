"""PyCSL mock for Python's signal module — Set handlers for asynchronous events."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def alarm(time: int) -> int:
    """Mock: If *time* is non-zero, this function requests that a :const:`SIGALRM` signal be sent to the process in *time* seconds. A..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsignal(signalnum: int) -> int:
    """Mock: Return the current signal handler for the signal *signalnum*. The returned value may be a callable Python object, or one..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def strsignal(signalnum: int) -> int:
    """Mock: Returns the description of signal *signalnum*, such as 'Interrupt' for :const:`SIGINT`. Returns :const:`None` if *signal..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def valid_signals() -> int:
    """Mock: Return the set of valid signal numbers on this platform.  This can be less than ``range(1, NSIG)`` if some signals are r..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pause() -> int:
    """Mock: Cause the process to sleep until a signal is received; the appropriate handler will then be called.  Returns nothing. ....."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def raise_signal(signum: int) -> int:
    """Mock: Sends a signal to the calling process. Returns nothing. .. versionadded:: 3.8"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pidfd_send_signal(pidfd: int, sig: int, siginfo: int, flags: int) -> int:
    """Mock: Send signal *sig* to the process referred to by file descriptor *pidfd*. Python does not currently support the *siginfo*..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def pthread_kill(thread_id: int, signalnum: int) -> int:
    """Mock: Send the signal *signalnum* to the thread *thread_id*, another thread in the same process as the caller.  The target thr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pthread_sigmask(how: int, mask: int) -> int:
    """Mock: Fetch and/or change the signal mask of the calling thread.  The signal mask is the set of signals whose delivery is curr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setitimer(which: int, seconds: int, interval: int) -> int:
    """Mock: Sets given interval timer (one of :const:`signal.ITIMER_REAL`, :const:`signal.ITIMER_VIRTUAL` or :const:`signal.ITIMER_P..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getitimer(which: int) -> int:
    """Mock: Returns current value of a given interval timer specified by *which*. .. availability:: Unix."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_wakeup_fd(fd: int, warn_on_full_buffer: int) -> int:
    """Mock: Set the wakeup file descriptor to *fd*.  When a signal your program has registered a signal handler for is received, the..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def siginterrupt(signalnum: int, flag: int) -> int:
    """Mock: Change system call restart behaviour: if *flag* is :const:`False`, system calls will be restarted when interrupted by si..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def signal(signalnum: int, handler: int) -> int:
    """Mock: Set the handler for signal *signalnum* to the function *handler*.  *handler* can be a callable Python object taking two ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sigpending() -> int:
    """Mock: Examine the set of signals that are pending for delivery to the calling thread (i.e., the signals which have been raised..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def sigwait(sigset: int) -> int:
    """Mock: Suspend execution of the calling thread until the delivery of one of the signals specified in the signal set *sigset*.  ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sigwaitinfo(sigset: int) -> int:
    """Mock: Suspend execution of the calling thread until the delivery of one of the signals specified in the signal set *sigset*.  ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sigtimedwait(sigset: int, timeout: int) -> int:
    """Mock: Like :func:`sigwaitinfo`, but takes an additional *timeout* argument specifying a timeout. If *timeout* is specified as ..."""
    return 0
