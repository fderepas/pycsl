# Formal tests for pycsl_lib/world — World model
# World class is the root state object. Test state concepts.


#@ ensures \result >= 0
def test_initial_processes() -> int:
    """Initial world has at least 0 processes."""
    return 0


#@ requires fd >= 0
#@ ensures \result >= 0
def test_fd_nonneg(fd: int) -> int:
    """File descriptors are non-negative."""
    return fd
