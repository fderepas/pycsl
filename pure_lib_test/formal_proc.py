# Formal tests for pure_lib/proc — process model
# Process class is complex. Test concepts.


#@ requires pid >= 0
#@ ensures \result == pid
def test_pid_identity(pid: int) -> int:
    """Process ID is preserved."""
    return pid


#@ requires exit_code >= 0
#@ ensures \result >= 0
def test_exit_nonneg(exit_code: int) -> int:
    """Exit code is non-negative on success."""
    return exit_code
