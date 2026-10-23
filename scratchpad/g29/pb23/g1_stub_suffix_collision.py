_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    def get(self) -> int:
        return 1


class D:
    def __init__(self) -> None:
        self.n = 2

    #@ ensures \result == 123
    def get(self) -> int:
        return 123


class E:
    def __init__(self) -> None:
        self.n = 3

    #@ ensures \result == 441
    def get(self) -> int:
        return 441


#@ ensures \result == 1
def f() -> int:
    o = C()
    return o.get()


#@ ensures \result == 123
def g() -> int:
    o = D()
    return o.get()


#@ ensures \result == 123
def h() -> int:
    o = E()
    return o.get()
