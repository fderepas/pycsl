class C:
    a: int
    b: int
    #@ assigns self.a, self.b
    def __init__(self) -> None:
        self.a = 5
        self.b = self.a

#@ ensures \result == 0
def f() -> int:
    c = C()
    return c.b
