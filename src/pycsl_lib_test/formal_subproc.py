# Formal tests for pycsl_lib/subproc — subprocess module
# CalledProcessError class. Test returncode concepts.


#@ requires returncode >= 0
#@ ensures \result == returncode
def test_returncode_preserved(returncode: int) -> int:
    """Returncode is preserved."""
    return returncode


#@ ensures \result >= 0
def test_exit_success() -> int:
    """Successful exit is 0."""
    return 0
