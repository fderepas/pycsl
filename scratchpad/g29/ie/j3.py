r"""missing key read of a parameter dict"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def f(d: Dict[str, int]) -> int:
    try:
        return d["zz"]
    except KeyError:
        return 9


#@ ensures \result == 0
def probe() -> int:
    return f({"a": 1})

if __name__ == "__main__":
    print("CPython:", probe())
