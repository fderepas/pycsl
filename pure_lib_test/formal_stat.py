# Formal tests for pure_lib/stat
from pure_lib.stat import S_ISDIR, S_ISREG, S_ISLNK, S_IMODE, S_IFMT


#@ requires mode >= 0
#@ ensures \result == 1 or \result == 0
def test_isdir_boolean(mode: int) -> int:
    """S_ISDIR returns 0 or 1."""
    return S_ISDIR(mode)


#@ requires mode >= 0
#@ ensures \result == 1 or \result == 0
def test_isreg_boolean(mode: int) -> int:
    """S_ISREG returns 0 or 1."""
    return S_ISREG(mode)


#@ requires mode >= 0
#@ ensures \result >= 0
#@ ensures \result < 4096
def test_imode_range(mode: int) -> int:
    """S_IMODE extracts low 12 bits (< 4096)."""
    return S_IMODE(mode)


#@ requires mode >= 0
#@ ensures \result >= 0
def test_ifmt_nonneg(mode: int) -> int:
    """S_IFMT is non-negative."""
    return S_IFMT(mode)
