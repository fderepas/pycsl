r"""subscript of an unmodelled call result"""
from typing import List, Dict, Any
_ = 0  # anchor


import json


#@ ensures \result == 0
def probe() -> int:
    d = json.loads("{}")
    return len(d)


if __name__ == "__main__":
    print("CPython:", probe())
