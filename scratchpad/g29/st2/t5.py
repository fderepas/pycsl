r"""dict len with duplicate keys"""
from typing import Set, List, Dict, FrozenSet
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    d: Dict[str, int] = {"a": 1, "a": 2}
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
