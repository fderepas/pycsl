class R:
    __slots__ = ("a",)
    def __init__(self, v: int) -> None:
        self.a = v
        self.b = v

#@ no_exception \all
#@ ensures \result == 3
def f() -> int:
    r = R(3)
    return r.a

if __name__ == "__main__":
    print(f())
