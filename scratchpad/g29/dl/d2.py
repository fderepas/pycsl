r"""del dict key then len"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    d: Dict[str, int] = {"a": 1, "b": 2}
    del d["a"]
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
