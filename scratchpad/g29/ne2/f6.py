r"""for over dict items with a 3-target unpack"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    for k, v, w in d.items():
        pass
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
