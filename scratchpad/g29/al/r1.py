r"""call-expression receiver"""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def sget(self) -> int:
        return self.x // self.x

    #@ requires d != 0
    #@ ensures \result == 1
    def get(self, d: int) -> int:
        return d // d


#@ ensures \result == 5
def probe() -> int:
    C(0).sget()
    return 5

if __name__ == "__main__":
    print("CPython:", probe())
