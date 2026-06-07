# Formal tests for pure_lib/fcmp — filecmp module
from pure_lib.fcmp import cmp, cmpfiles_match, cmpfiles_mismatch


#@ requires size >= 0
#@ ensures \result >= 0
def test_cmp_nonneg(size: int) -> int:
    """cmp returns non-negative."""
    return cmp(size, size)


#@ requires count >= 0
#@ ensures \result >= 0
def test_match_nonneg(count: int) -> int:
    """Match count is non-negative."""
    return cmpfiles_match(count)


#@ requires count >= 0
#@ ensures \result >= 0
def test_mismatch_nonneg(count: int) -> int:
    """Mismatch count is non-negative."""
    return cmpfiles_mismatch(count)
