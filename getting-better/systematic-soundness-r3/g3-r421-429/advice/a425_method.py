#@ class invariant self.n >= 0
class A:
    #@ requires n >= 0
    def __init__(self, n: int) -> None:
        self.n = n

    #@ requires n >= 0
    #@ assigns self.n
    def reset(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 0
    #@ assigns \nothing
    def where(self) -> int:
        return self.n


#@ ensures \result >= 0
def g(a: A) -> int:
    a.reset(4)
    return a.where()
