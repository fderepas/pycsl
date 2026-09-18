r"""dict literal duplicate key last wins"""
from typing import Set, List, Dict, FrozenSet
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, int] = {"a": 1, "a": 2}
    return d["a"]


if __name__ == "__main__":
    print("CPython:", probe())
