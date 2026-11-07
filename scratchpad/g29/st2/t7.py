r"""frozenset equality ignoring order"""
from typing import Set, List, Dict, FrozenSet
_ = 0  # anchor


#@ ensures \result == False
def probe() -> bool:
    return frozenset([1, 2]) == frozenset([2, 1])


if __name__ == "__main__":
    print("CPython:", probe())
