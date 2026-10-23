import lib5
from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    return lib5.get(d) * 0


if __name__ == "__main__":
    print("CPython:", probe())
