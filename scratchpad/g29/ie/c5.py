r"""nested dict missing inner key caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, Dict[str, int]] = {"a": {"x": 1}}
    try:
        v = d["a"]["y"]
    except KeyError:
        return 9
    return v


if __name__ == "__main__":
    print("CPython:", probe())
