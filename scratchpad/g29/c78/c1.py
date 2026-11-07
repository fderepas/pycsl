r"""callee int() of bad string caught"""
from typing import List, Dict, Tuple
_ = 0  # anchor


def parse(s: str) -> int:
    return int(s)


#@ ensures \result == 0
def probe() -> int:
    try:
        v = parse("x")
    except ValueError:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
