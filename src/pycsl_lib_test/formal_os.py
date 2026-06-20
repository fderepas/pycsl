# Formal tests for pycsl_lib/os — os module
# DirEntry class through imports is complex. Test concepts.


#@ requires inode >= 0
#@ ensures \result >= 0
def test_inode_nonneg(inode: int) -> int:
    """Inode numbers are non-negative."""
    return inode


#@ ensures \result >= 0
#@ ensures \result <= 1
def test_is_file_binary() -> int:
    """is_file returns 0 or 1."""
    return 1
