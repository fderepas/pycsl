r"""missing key read OUTSIDE the try in a function with a KeyError handler, user no_exception KeyError"""
from typing import Dict
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    w = d["zz"]
    try:
        v = d["a"]
    except KeyError:
        return 9
    return w * 0


if __name__ == "__main__":
    print("CPython:", probe())
