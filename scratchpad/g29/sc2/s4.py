r"""with as binding persists"""
from typing import List
_ = 0  # anchor


class CM:
    def __init__(self) -> None:
        self.v = 5

    def __enter__(self) -> int:
        return 5

    def __exit__(self, a: object, b: object, c: object) -> bool:
        return False


#@ ensures \result == 0
def probe() -> int:
    v = 0
    with CM() as v:
        pass
    return v


if __name__ == "__main__":
    print("CPython:", probe())
