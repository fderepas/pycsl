# Formal tests for pycsl_lib/sig — signal module model
from pycsl_lib.sig import signal_handler, getsignal, valid_signals_count, strsignal


#@ requires sig_num >= 1 and sig_num <= 64
#@ requires handler >= 0
#@ ensures \result >= 0
def test_signal_returns_prev(sig_num: int, handler: int) -> int:
    """signal() returns previous handler (non-negative)."""
    return signal_handler(sig_num, handler)


#@ requires sig_num >= 1 and sig_num <= 64
#@ ensures \result >= 0
def test_getsignal_nonneg(sig_num: int) -> int:
    """getsignal returns non-negative handler id."""
    return getsignal(sig_num)


#@ ensures \result > 0
def test_valid_signals_positive() -> int:
    """At least one signal exists."""
    return valid_signals_count()


#@ requires sig_num >= 1 and sig_num <= 64
#@ ensures \result >= 0
#@ ensures \result <= sig_num
def test_strsignal_bounded(sig_num: int) -> int:
    """strsignal name length bounded by signal number."""
    return strsignal(sig_num)
