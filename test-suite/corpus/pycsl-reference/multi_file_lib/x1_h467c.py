"""Helper for corpus 7272 (route #467): getattr of a missing attribute."""


def g(x: int) -> int:
    return getattr(x, "zz")
