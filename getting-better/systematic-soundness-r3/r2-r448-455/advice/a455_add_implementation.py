# advice probe (route #455): witness 6968 with the implementation added after the stub -- must VERIFY
from typing import overload


@overload
def g(a: int) -> int:
    ...


def g(a: int) -> int:
    return a


#@ no_exception \all
def f(n: int) -> int:
    return g(n)
