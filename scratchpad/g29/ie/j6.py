r"""missing key deleted then read in try"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    del d["a"]
    try:
        v = d["a"]
    except KeyError:
        return 9
    return v

if __name__ == "__main__":
    print("CPython:", probe())
