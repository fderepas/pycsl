r"""ok control: satisfied requires via receiver"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    #@ requires d != 0
    #@ ensures \result == 1
    def get(self, d: int) -> int:
        return d // d

    #@ requires self.x != 0
    #@ ensures \result == 1
    def sget(self) -> int:
        return self.x // self.x


#@ ensures \result == 1
def probe() -> int:
    c = C(3)
    return c.sget()

if __name__ == "__main__":
    print("CPython:", probe())
