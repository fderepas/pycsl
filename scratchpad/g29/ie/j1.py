r"""missing key read, no try"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    return d["b"]

if __name__ == "__main__":
    print("CPython:", probe())
