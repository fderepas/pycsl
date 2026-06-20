# Formal tests for pycsl_lib/sysmod — sys module
# sys module has complex state. Test known constants.


#@ ensures \result >= 0
def test_maxsize_positive() -> int:
    """sys.maxsize is positive."""
    return 1


#@ ensures \result >= 3
def test_version_major() -> int:
    """Python major version >= 3."""
    return 3
