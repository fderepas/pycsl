r"""implicit KeyError caught"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        v = d["b"]
    except KeyError:
        return 9
    return v

if __name__ == "__main__":
    print("CPython:", probe())
