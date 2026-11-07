from typing import Dict
from helper178 import get
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    v = get(d)
    return v * 0


if __name__ == "__main__":
    print("CPython:", probe())
