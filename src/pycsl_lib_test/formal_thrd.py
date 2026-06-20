# Formal tests for pycsl_lib/thrd — threading module
from pycsl_lib.thrd import active_count, current_thread


#@ ensures \result >= 1
def test_active_at_least_one() -> int:
    """At least one thread (main) is active."""
    return active_count()


#@ ensures \result >= 0
def test_current_nonneg() -> int:
    """current_thread returns non-negative."""
    return current_thread()
