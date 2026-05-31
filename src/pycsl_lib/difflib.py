"""PyCSL mock for Python's difflib module — Helpers for computing differences between objects."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/difflib.html#difflib.context_diff
#@ ensures True
def context_diff(a: int, b: int, fromfile: int, tofile: int, fromfiledate: int, tofiledate: int, n: int) -> int:
    """Mock: Compare *a* and *b* (lists of strings); return a delta (a :term:`generator` generating the delta lines) in context diff ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/difflib.html#difflib.get_close_matches
#@ requires n > 0
#@ requires 0 <= cutoff
#@ requires cutoff <= 1
#@ ensures \result >= 0
#@ ensures \result <= n
def get_close_matches(word: int, possibilities: int, n: int, cutoff: int) -> int:
    """Mock: Return a list of the best 'good enough' matches.  *word* is a sequence for which close matches are desired (typically a ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/difflib.html#difflib.ndiff
#@ ensures True
def ndiff(a: int, b: int, linejunk: int, charjunk: int) -> int:
    """Mock: Compare *a* and *b* (lists of strings); return a :class:`Differ`\ -style delta (a :term:`generator` generating the delta..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/difflib.html#difflib.restore
# cite:_note: returns a generator of str lines; output sequence semantics exceed expressible contract surface for this int-typed stub
#@ requires which == 1 or which == 2
#@ ensures True
def restore(sequence: int, which: int) -> int:
    """Mock: Return one of the two sequences that generated a delta. Given a *sequence* produced by :meth:`Differ.compare` or :func:`..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/difflib.html#difflib.unified_diff
#@ requires n >= 0
#@ ensures True
def unified_diff(a: int, b: int, fromfile: int, tofile: int, fromfiledate: int, tofiledate: int, n: int) -> int:
    """Mock: Compare *a* and *b* (lists of strings); return a delta (a :term:`generator` generating the delta lines) in unified diff ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/difflib.html#difflib.diff_bytes
#@ ensures True
def diff_bytes(dfunc: int, a: int, b: int, fromfile: int, tofile: int, fromfiledate: int, tofiledate: int) -> int:
    """Mock: Compare *a* and *b* (lists of bytes objects) using *dfunc*; yield a sequence of delta lines (also bytes) in the format r..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/difflib.html#difflib.IS_LINE_JUNK
#@ ensures \result == 0 or \result == 1
def IS_LINE_JUNK(line: int) -> int:
    """Mock: Return ``True`` for ignorable lines.  The line *line* is ignorable if *line* is blank or contains a single ``'#'``, othe..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/difflib.html#difflib.IS_CHARACTER_JUNK
#@ ensures (ch == 32 or ch == 9) ==> \result == 1
#@ ensures (ch != 32 and ch != 9) ==> \result == 0
def IS_CHARACTER_JUNK(ch: int) -> int:
    """Mock: Return ``True`` for ignorable characters.  The character *ch* is ignorable if *ch* is a space or tab, otherwise it is no..."""
    return 0
