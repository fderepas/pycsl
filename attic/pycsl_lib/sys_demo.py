"""Formal driver for the sys stub (the my_os_demo.py analog).

Exercises the side-effect (`result == 0`) and query (`result >= 0`) contracts end-to-end.
Verifies with **zero** `\trusted` — each wrapper's postcondition is discharged from the callee's
`ensures`."""
from sys import getrecursionlimit, getsizeof, setrecursionlimit, exit


#@ ensures \result >= 0
def demo_recursion_limit() -> int:
    """A query function returns a non-negative value."""
    return getrecursionlimit()


#@ ensures \result >= 0
def demo_sizeof(obj: int) -> int:
    """getsizeof returns a non-negative byte count (default arg passed explicitly)."""
    return getsizeof(obj, 0)


#@ ensures \result == 0
def demo_set_limit(n: int) -> int:
    """A side-effect setter returns 0."""
    return setrecursionlimit(n)


#@ ensures \result == 0
def demo_exit() -> int:
    """exit() returns 0 in the mock."""
    return exit(0)
