"""Helper for corpus 7263 (route #466): an MRO conflict at class creation."""


class A:
    pass


class B(A):
    pass


class Z(A, B):
    pass


def g(x: int) -> int:
    return x
