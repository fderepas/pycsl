r"""augmented assign on dict value"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    d["a"] += 2
    return d["a"]


if __name__ == "__main__":
    print("CPython:", probe())
