r"""missing key in finally"""
from typing import Dict, List
_ = 0  # anchor


#@ ensures \result == 9
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    r = 0
    try:
        r = 9
    except KeyError:
        r = 9
    finally:
        v = d["b"]
    return r


if __name__ == "__main__":
    print("CPython:", probe())
