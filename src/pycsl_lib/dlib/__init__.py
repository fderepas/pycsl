# Pure model for difflib — sequence comparison
# Models SequenceMatcher ratio and diff counts.

""" # pycsl"""


#@ class invariant self._len_a >= 0
#@ class invariant self._len_b >= 0
class SequenceMatcher:
    """Abstract sequence matcher tracking input lengths."""

    #@ requires len_a >= 0
    #@ requires len_b >= 0
    #@ ensures self._len_a == len_a
    #@ ensures self._len_b == len_b
    def __init__(self, len_a: int, len_b: int) -> None:
        self._len_a: int = len_a
        self._len_b: int = len_b

    #@ ensures \result >= 0
    def ratio(self) -> int:
        """Similarity ratio * 1000 (0..1000 range)."""
        return 0

    #@ ensures \result >= 0
    #@ ensures \result <= self._len_a + self._len_b
    def get_opcodes_count(self) -> int:
        """Number of edit operations."""
        return self._len_a + self._len_b


#@ requires len_a >= 0
#@ requires len_b >= 0
#@ ensures \result >= 0
def unified_diff_lines(len_a: int, len_b: int) -> int:
    """Count of unified diff output lines."""
    return len_a + len_b


#@ requires len_a >= 0
#@ requires len_b >= 0
#@ ensures \result >= 0
def context_diff_lines(len_a: int, len_b: int) -> int:
    """Count of context diff output lines."""
    return len_a + len_b


#@ requires len_a >= 0
#@ requires len_b >= 0
#@ ensures \result >= 0
def ndiff_lines(len_a: int, len_b: int) -> int:
    """Count of ndiff output lines."""
    return len_a + len_b


#@ requires cutoff >= 0
#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures \result <= n
def get_close_matches(cutoff: int, n: int) -> int:
    """Return at most n close matches."""
    return n
