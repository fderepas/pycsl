# pure_lib/sig — pure-Python signal module model
# Named 'sig' to avoid stdlib name clash.
#
# Contracts derived from library_reference/signal.rst.
# RST: "Set the handler for signal signalnum to the function handler."
# RST: "Return the current signal handler for the signal signalnum."
# RST: "Return the set of valid signal numbers on this platform."
# RST: "Sigset — set of signals."

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
    """RST: 'Set the handler for signal signalnum to the function handler.'
    Returns the previous handler (non-negative id). SIG_DFL = 0."""
    return SIG_DFL


#@ requires sig_num >= 1 and sig_num <= 64
#@ ensures \result >= 0
def getsignal(sig_num: int) -> int:
    """RST: 'Return the current signal handler for the signal signalnum.
    The returned value may be SIG_IGN, SIG_DFL, or None.' -> non-negative."""
    return SIG_DFL


#@ requires sig_num >= 1 and sig_num <= 64
def raise_signal(sig_num: int) -> None:
    """RST: 'Send a signal to the calling process.' No return value."""
    pass


#@ ensures \result > 0
def valid_signals_count() -> int:
    """RST: 'Return the set of valid signal numbers on this platform.'
    At least 1 signal exists on any platform."""
    return 64


#@ requires sig_num >= 1 and sig_num <= 64
#@ ensures \result >= 0
#@ ensures \result <= sig_num
def strsignal(sig_num: int) -> int:
    """RST: 'Return the system description of the signal signalnum.'
    Returns description length (bounded by signal number for model)."""
    return sig_num


# --- Sigset class ---

""  # pycsl
#@ class invariant self._count >= 0
#@ class invariant self._count <= 64
class Sigset:
    """Model of a signal set (used for pthread_sigmask, etc.)."""

    def __init__(self):
        self._count = 0

    #@ requires sig_num >= 1 and sig_num <= 64
    #@ ensures self._count <= 64
    #@ assigns self._count
    def add(self, sig_num: int) -> None:
        """Add a signal to the set."""
        if self._count < 64:
            self._count = self._count + 1

    #@ requires sig_num >= 1 and sig_num <= 64
    #@ ensures self._count >= 0
    #@ assigns self._count
    def discard(self, sig_num: int) -> None:
        """Remove a signal from the set (if present)."""
        if self._count > 0:
            self._count = self._count - 1

    #@ ensures \result == self._count
    #@ assigns \nothing
    def size(self) -> int:
        """Number of signals in the set."""
        return self._count
