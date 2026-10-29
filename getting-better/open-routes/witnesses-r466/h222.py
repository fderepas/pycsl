class A:
    pass


class B(A):
    pass


class Z(A, B):
    pass


def g(x: int) -> int:
    return x
