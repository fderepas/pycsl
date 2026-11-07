r"""conditional expression missing key in return"""
from typing import Dict, List
_ = 0  # anchor


#@ no_exception KeyError
#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    return 0 if d["b"] > 0 else 0


if __name__ == "__main__":
    print("CPython:", probe())
