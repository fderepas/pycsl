class C:
    b: bool
    #@ assigns self.b
    def __init__(self, v: bool) -> None:
        self.b = v

#@ ensures \result == 1
def f() -> int:
    c = C(1)
    if c.b is True:
        return 1
    return 0
