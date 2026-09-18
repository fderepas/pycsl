r"""missing key in else not caught by own handler"""
from typing import Dict, List
_ = 0  # anchor


#@ ensures \result == 9
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        x = 1
    except KeyError:
        return 9
    else:
        v = d["b"]
    return 9


if __name__ == "__main__":
    print("CPython:", probe())
