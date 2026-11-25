from zv83o5c.k import three


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g() -> int:
    c = C()
    return c.b + three()


print("result", g())
