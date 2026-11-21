r"""dict of strings missing key caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, str] = {"a": "x"}
    try:
        v = d["b"]
    except KeyError:
        return 9
    return len(v)


if __name__ == "__main__":
    print("CPython:", probe())
