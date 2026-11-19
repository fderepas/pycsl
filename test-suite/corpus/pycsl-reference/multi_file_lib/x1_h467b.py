"""Helper for corpus 7271 (route #467): next() of an empty iterator."""


def g(x: int) -> int:
    return x + next(iter([]))
