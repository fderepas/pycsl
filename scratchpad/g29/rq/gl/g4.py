r"""local mutator expr stmt, field read"""
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


#@ ensures \result == 0
def probe() -> int:
    c = C(0)
    c.bump()
    return c.x

if __name__ == "__main__":
    print("CPython:", probe())
