class Counter:
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def __enter__(self) -> int:
        self.n = self.n + 1
        return 0

    #@ ensures \result == False
    #@ assigns \nothing
    def __exit__(self, a: object, b: object, c: object) -> bool:
        return False


#@ ensures \result == 0
def f() -> int:
    c = Counter()
    with c:
        pass
    return c.n


if __name__ == "__main__":
    print("CPython f() =", f())
