"""PyCSL mock for Python's re module — Regular expression operations."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def compile(pattern: int, flags: int) -> int:
    """Mock: Compile a regular expression pattern into a :ref:`regular expression object <re-objects>`, which can be used for matchin..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def search(pattern: int, string: int, flags: int) -> int:
    """Mock: Scan through *string* looking for the first location where the regular expression *pattern* produces a match, and return..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prefixmatch(pattern: int, string: int, flags: int) -> int:
    """Mock: If zero or more characters at the beginning of *string* match the regular expression *pattern*, return a corresponding :..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def match(pattern: int, string: int, flags: int) -> int:
    """Mock: .. soft-deprecated:: 3.15 :func:`~re.match` has been :term:`soft deprecated` in favor of the alternate :func:`~re.prefix..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fullmatch(pattern: int, string: int, flags: int) -> int:
    """Mock: If the whole *string* matches the regular expression *pattern*, return a corresponding :class:`~re.Match`.  Return ``Non..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def split(pattern: int, string: int, maxsplit: int, flags: int) -> int:
    """Mock: Split *string* by the occurrences of *pattern*.  If capturing parentheses are used in *pattern*, then the text of all gr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def findall(pattern: int, string: int, flags: int) -> int:
    """Mock: Return all non-overlapping matches of *pattern* in *string*, as a list of strings or tuples.  The *string* is scanned le..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def finditer(pattern: int, string: int, flags: int) -> int:
    """Mock: Return an :term:`iterator` yielding :class:`~re.Match` objects over all non-overlapping matches for the RE *pattern* in ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sub(pattern: int, repl: int, string: int, count: int, flags: int) -> int:
    """Mock: Return the string obtained by replacing the leftmost non-overlapping occurrences of *pattern* in *string* by the replace..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def subn(pattern: int, repl: int, string: int, count: int, flags: int) -> int:
    """Mock: Perform the same operation as :func:`sub`, but return a tuple ``(new_string, number_of_subs_made)``. The expression's be..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def escape(pattern: int) -> int:
    """Mock: Escape special characters in *pattern*. This is useful if you want to match an arbitrary literal string that may have re..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def purge() -> int:
    """Mock: Clear the regular expression cache."""
    return 0
