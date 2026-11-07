r"""no_exception KeyError over dict comprehension"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    e = {k: d[k] for k in ["b"]}
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
