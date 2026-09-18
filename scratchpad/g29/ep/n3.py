r"""no_exception all with a call to a helper reading a dict"""
from typing import List, Dict
_ = 0  # anchor


def get(d: Dict[str, int]) -> int:
    return d["a"]


#@ no_exception \all
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    return get(d) * 0


if __name__ == "__main__":
    print("CPython:", probe())
