"""Helper for corpus 7270 (route #467): an un-claimed function whose assert fails."""


def g(x: int) -> int:
    assert x != x
    return x
