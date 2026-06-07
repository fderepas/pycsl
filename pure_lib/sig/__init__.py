# pure_lib/sig — pure-Python signal module model
# Named 'sig' to avoid stdlib name clash.
#
# Models signal constants and handler registration.
# Contract-only: all dispatch is C-runtime backed.

# Signal number constants (POSIX subset)
SIGHUP = 1
SIGINT = 2
SIGQUIT = 3
SIGABRT = 6
SIGKILL = 9
SIGTERM = 15
SIGCHLD = 17
SIGCONT = 18
SIGSTOP = 19

# Special handler values
SIG_DFL = 0
SIG_IGN = 1


#@ requires sig_num >= 1 and sig_num <= 64
#@ requires handler >= 0
#@ ensures \result >= 0
def signal_handler(sig_num: int, handler: int) -> int:
    """Register a signal handler. Returns the previous handler.
    Model: handler is an opaque id; returns old handler id."""
    return SIG_DFL


#@ requires sig_num >= 1 and sig_num <= 64
#@ ensures \result >= 0
def getsignal(sig_num: int) -> int:
    """Get current handler for signal. Returns handler id."""
    return SIG_DFL


#@ requires sig_num >= 1 and sig_num <= 64
def raise_signal(sig_num: int) -> None:
    """Raise a signal in the current process."""
    pass


#@ ensures \result >= 0
def valid_signals_count() -> int:
    """Return count of valid signals on this platform."""
    return 64
