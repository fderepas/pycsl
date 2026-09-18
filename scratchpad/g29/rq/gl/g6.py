r"""global plain function call on global"""
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires self.x != 0
    #@ ensures \result == 1
    def sget(self) -> int:
        return self.x // self.x

    #@ assigns self.x
    def bump(self) -> None:
        self.x = self.x + 1


_g = C(0)


#@ ensures \result == 5
def probe() -> int:
    print(_g.sget())
    return 5

if __name__ == "__main__":
    print("CPython:", probe())
