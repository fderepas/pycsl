class R:
    __slots__ = ("x",)
    def __init__(self) -> None:
        self.x = 0
        self.y = 1

#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    r = R()
    return r.y

if __name__ == "__main__":
    print(f())
