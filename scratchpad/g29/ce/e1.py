r"""computed rhs from an unmodelled call"""
from typing import List, Dict, Any
_ = 0  # anchor


import json


#@ ensures \result == 0
def probe() -> int:
    v = json.dumps([1])
    return len(v)


if __name__ == "__main__":
    print("CPython:", probe())
