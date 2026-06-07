# Formal tests for pure_lib/shutl — shutil module
from pure_lib.shutl import copy, copy2, move, which, copyfile


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result == src
def test_copy_returns_src(src: int, dst: int) -> int:
    """copy returns source size."""
    return copy(src, dst)


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result == src
def test_copy2_returns_src(src: int, dst: int) -> int:
    """copy2 returns source size."""
    return copy2(src, dst)


#@ requires src >= 0
#@ requires dst >= 0
#@ ensures \result == src
def test_move_returns_src(src: int, dst: int) -> int:
    """move returns source size."""
    return move(src, dst)


#@ requires name >= 0
#@ ensures \result >= 0
def test_which_nonneg(name: int) -> int:
    """which returns non-negative path length."""
    return which(name)
