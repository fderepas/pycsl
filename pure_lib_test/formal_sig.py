# Formal test for signal (sig) module
#
# Based on library_reference/signal.rst:
#   "Set the handler for signal signalnum to the function handler."
#   "Return the current signal handler for the signal signalnum."
#
# Tests verify contract postconditions:
#   - signal_handler: ensures result >= 0
#   - getsignal: ensures result >= 0
#   - valid_signals_count: ensures result >= 0

from pure_lib.sig import signal_handler, getsignal, valid_signals_count


#@ ensures \result >= 0
def test_signal_handler_nonneg() -> int:
    """signal_handler returns non-negative (old handler)."""
    return signal_handler(2, 1)


#@ ensures \result >= 0
def test_getsignal_nonneg() -> int:
    """getsignal returns non-negative (current handler)."""
    return getsignal(15)


#@ ensures \result >= 0
def test_valid_signals_nonneg() -> int:
    """Platform signal count is non-negative."""
    return valid_signals_count()
