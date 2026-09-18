r"""raise in else of try"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    try:
        v = 1
    except ValueError:
        return 5
    else:
        raise ValueError("x")
    return v

if __name__ == "__main__":
    print("CPython:", probe())
