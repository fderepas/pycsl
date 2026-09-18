r"""staticmethod call on instance"""
from typing import List
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 1

    @staticmethod
    def f(x: int) -> int:
        return x + 1


#@ ensures \result == 5
def probe() -> int:
    c = C()
    return c.f(5)


if __name__ == "__main__":
    print("CPython:", probe())
