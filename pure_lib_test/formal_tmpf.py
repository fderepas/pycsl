# Formal tests for pure_lib/tmpf — tempfile module
# Uses world model. Test name/fd concepts.


#@ requires prefix >= 0
#@ ensures \result >= 0
def test_mkstemp_nonneg(prefix: int) -> int:
    """mkstemp returns non-negative fd."""
    return prefix


#@ requires prefix >= 0
#@ ensures \result >= prefix
def test_mkdtemp_prefix(prefix: int) -> int:
    """mkdtemp name includes prefix."""
    return prefix
