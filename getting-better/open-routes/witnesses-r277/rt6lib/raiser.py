#@ ensures \result == 0
#@ assigns \nothing
def f(k: int) -> int:
    if k > 0:
        raise ValueError("x")
    return 0

#@ ensures \result == 0
#@ assigns \nothing
def h(k: int) -> int:
    return f(k)

class A:
    def __init__(self) -> None:
        self.v: int = 0
    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self, k: int) -> int:
        if k > 0:
            raise KeyError("x")
        return 0

#@ ensures \result == 0
#@ assigns \nothing
def viaA(k: int) -> int:
    return A().m(k)

#@ ensures \result == 0
#@ assigns \nothing
def idx(xs: list, k: int) -> int:
    return xs[k] * 0
