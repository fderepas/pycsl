# Formal tests for pycsl_lib/unt — unittest module
# Class through imports loses precision.


#@ requires tests >= 0
#@ requires failures >= 0
#@ ensures \result == tests + 1
def test_add_success(tests: int, failures: int) -> int:
    """addSuccess increments test count."""
    return tests + 1


#@ requires tests >= 0
#@ ensures \result >= 0
#@ ensures \result <= 1
def test_successful_when_zero_failures(tests: int) -> int:
    """wasSuccessful is 1 when no failures."""
    return 1
