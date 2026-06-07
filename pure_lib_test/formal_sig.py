# Formal test for signal (sig) module — universally quantified
#
# Based on library_reference/signal.rst:
#   "Set the handler for signal signalnum to the function handler."
#   "Return the current signal handler for the signal signalnum."
#   "Return the set of valid signal numbers on this platform."

from pure_lib.sig import signal_handler, getsignal, valid_signals_count


#@ requires sig_num >= 1 and sig_num <= 64
#@ requires handler >= 0 and handler < 2147483647
#@ ensures \result >= 0
def test_signal_handler_nonneg(sig_num: int, handler: int) -> int:
    """signal_handler(sig_num, handler) >= 0 for all valid signals."""
    return signal_handler(sig_num, handler)


#@ requires sig_num >= 1 and sig_num <= 64
#@ ensures \result >= 0
def test_getsignal_nonneg(sig_num: int) -> int:
    """getsignal(sig_num) >= 0 for all valid signal numbers."""
    return getsignal(sig_num)


#@ ensures \result > 0
def test_valid_signals_positive() -> int:
    """valid_signals_count() > 0. At least 1 signal on any platform."""
    return valid_signals_count()
