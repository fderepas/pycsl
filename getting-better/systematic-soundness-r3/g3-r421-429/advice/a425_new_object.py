#@ class invariant self.n >= 0
class A:
    #@ requires n >= 0
    def __init__(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 0
    #@ assigns \nothing
    def where(self) -> int:
        return self.n


#@ ensures \result >= 0
def g(a: A) -> int:
    b = A(4)
    return b.where()
