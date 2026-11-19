class R:
    __slots__ = ["x"]
    def __init__(self) -> None:
        self.x = 0
        self.y = 0

#@ no_exception \all
#@ ensures \result == 0
def f() -> int:
    r = R()
    return r.x

if __name__ == "__main__":
    print(f())
