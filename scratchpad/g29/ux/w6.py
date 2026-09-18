r"""eq dunder raising caught"""
from typing import List, Dict
_ = 0  # anchor


class S:
    def __init__(self) -> None:
        self.k = 0

    def __eq__(self, o: object) -> bool:
        raise ValueError()


#@ ensures \result == 0
def probe() -> int:
    try:
        b = S() == S()
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
