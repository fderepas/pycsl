"""PyCSL mock for Python's fnmatch module — Unix shell style filename pattern matching."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def fnmatch(name: int, pat: int) -> int:
    """Mock: Test whether the filename string *name* matches the pattern string *pat*, returning ``True`` or ``False``.  Both paramet..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fnmatchcase(name: int, pat: int) -> int:
    """Mock: Test whether the filename string *name* matches the pattern string *pat*, returning ``True`` or ``False``; the compariso..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def filter(names: int, pat: int) -> int:
    """Mock: Construct a list from those elements of the :term:`iterable` of filename strings *names* that match the pattern string *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def filterfalse(names: int, pat: int) -> int:
    """Mock: Construct a list from those elements of the :term:`iterable` of filename strings *names* that do not match the pattern s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def translate(pat: int) -> int:
    """Mock: Return the shell-style pattern *pat* converted to a regular expression for using with :func:`re.prefixmatch`. The patter..."""
    return 0
