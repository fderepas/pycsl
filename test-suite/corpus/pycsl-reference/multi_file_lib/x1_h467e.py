"""Helper for corpus 7274 (route #467): an assert in a SECOND helper of the module."""


def k(x: int) -> int:
    assert x < 0
    return x


def g(x: int) -> int:
    return k(x)
