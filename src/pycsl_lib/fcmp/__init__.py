# Pure model for filecmp — file and directory comparison
# Models as boolean comparison results.


#@ requires size_a >= 0
#@ requires size_b >= 0
#@ ensures \result >= 0
#@ ensures \result <= 1
def cmp(size_a: int, size_b: int) -> int:
    """Compare two files. Returns 1 if equal, 0 if different."""
    if size_a == size_b:
        return 1
    return 0


#@ requires count >= 0
#@ ensures \result >= 0
#@ ensures \result <= count
def cmpfiles_match(count: int) -> int:
    """Count of matching files in directory comparison."""
    return count


#@ requires count >= 0
#@ ensures \result >= 0
#@ ensures \result <= count
def cmpfiles_mismatch(count: int) -> int:
    """Count of mismatched files."""
    return 0


#@ requires count >= 0
#@ ensures \result >= 0
#@ ensures \result <= count
def cmpfiles_errors(count: int) -> int:
    """Count of files that couldn't be compared."""
    return 0
