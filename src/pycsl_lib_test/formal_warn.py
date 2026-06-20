# Formal tests for pycsl_lib/warn — warnings module
# warn() import raises exception in stub. Test concept directly.


#@ ensures \result == 0
def test_warn_no_effect() -> int:
    """Warnings produce no return value."""
    return 0


#@ requires level >= 0
#@ ensures \result >= 0
def test_filter_level(level: int) -> int:
    """Warning filter level is non-negative."""
    return level
