class C:
    a: int
    b: int

    #@ assigns self.a, self.b
    def __init__(self, n: int) -> None:
        self.a = n
        self.b = self.a + 1


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    c = C(5)
    return c.b
