r"""G29 SM3 — two classes' `get` methods called through the SAME receiver NAME in two functions:
the abstract stubs are both named `o_get_0`, and `_add_abstract_op` keeps the LONGER declaration."""
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

    #@ ensures \result == 700
    def get(self) -> int:
        return 700


#@ ensures \result == 700
def f() -> int:
    o = C()
    return o.get()


#@ ensures \result == 700
def g() -> int:
    o = D()
    return o.get()


if __name__ == "__main__":
    print("CPython:", f(), g())
