class A:
    def __init__(self):
        self.n: int = 0

    #@ requires True
    #@ ensures \result == 1
    def f(self) -> int:
        return 1


class B(A):
    #@ requires True
    #@ ensures \result == 2
    def f(self) -> int:
        return 2


#@ ensures \result == 1
def probe() -> int:
    b = B()
    return b.f()
