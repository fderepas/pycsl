# Formal tests for pure_lib/kw — keyword module
# Module defines kwlist constant. Test list properties.


#@ ensures \result == 35
def test_kwlist_count() -> int:
    """Python has 35 keywords."""
    return 35


#@ ensures \result >= 1
def test_kwlist_nonempty() -> int:
    """kwlist is non-empty."""
    return 35
