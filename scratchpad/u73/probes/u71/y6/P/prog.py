from zuy6.k import three


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g() -> int:
    c = C()
    f = three
    return c.b + f()


print("result", g())
