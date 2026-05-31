"""PyCSL mock for Python's fnmatch module — Unix shell style filename pattern matching."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatch
#@ ensures \result == 0 or \result == 1
def fnmatch(name: int, pat: int) -> int:
    """Mock: Test whether the filename string *name* matches the pattern string *pat*, returning ``True`` or ``False``.  Both paramet..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fnmatch.html#fnmatch.fnmatchcase
#@ ensures \result == 0 or \result == 1
def fnmatchcase(name: int, pat: int) -> int:
    """Mock: Test whether the filename string *name* matches the pattern string *pat*, returning ``True`` or ``False``; the compariso..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fnmatch.html#fnmatch.filter
#@ requires names >= 0
#@ ensures \result >= 0
#@ ensures \result <= names
def filter(names: int, pat: int) -> int:
    """Mock: Construct a list from those elements of the :term:`iterable` of filename strings *names* that match the pattern string *..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fnmatch.html#fnmatch.filterfalse
#@ ensures \result >= 0
#@ ensures \result <= names
def filterfalse(names: int, pat: int) -> int:
    """Mock: Construct a list from those elements of the :term:`iterable` of filename strings *names* that do not match the pattern s..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/fnmatch.html#fnmatch.translate
# cite:_note: doc semantics (shell pattern → regex string) exceed expressible contract surface for this int stub
#@ ensures \result >= 0
def translate(pat: int) -> int:
    """Mock: Return the shell-style pattern *pat* converted to a regular expression for using with :func:`re.prefixmatch`. The patter..."""
    return 0
