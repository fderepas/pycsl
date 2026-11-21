r"""context manager enter raising caught"""
from typing import List, Dict
_ = 0  # anchor


class CM:
    def __init__(self) -> None:
        self.k = 0

    def __enter__(self) -> "CM":
        raise ValueError()

    def __exit__(self, a: object, b: object, c: object) -> bool:
        return False


#@ ensures \result == 0
def probe() -> int:
    try:
        with CM():
            pass
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
