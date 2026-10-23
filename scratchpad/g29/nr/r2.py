r"""NoReturn method that returns"""
from typing import List, NoReturn
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.k = 0

    def die(self) -> NoReturn:
        return None


#@ ensures \result == 1
def probe() -> int:
    c = C()
    c.die()
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
