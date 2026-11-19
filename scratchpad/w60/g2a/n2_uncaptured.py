def mk() -> str:
    return "zz"


class C:
    s: str

    #@ assigns self.s
    def __init__(self) -> None:
        self.s: str = mk()


#@ requires True
#@ ensures \result == ""
#@ assigns \nothing
def f() -> str:
    c = C()
    return c.s
