"""PyCSL mock for Python's filecmp module — Compare files efficiently."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def cmp(f1: int, f2: int, shallow: int) -> int:
    """Mock: Compare the files named *f1* and *f2*, returning ``True`` if they seem equal, ``False`` otherwise. If *shallow* is true ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cmpfiles(dir1: int, dir2: int, common: int, shallow: int) -> int:
    """Mock: Compare the files in the two directories *dir1* and *dir2* whose names are given by *common*. Returns three lists of fil..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def clear_cache() -> int:
    """Mock: Clear the filecmp cache. This may be useful if a file is compared so quickly after it is modified that it is within the ..."""
    return 0
