r"""get of missing key in dict of dicts"""
from typing import Dict, List, Set, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, Dict[str, int]] = {"a": {"x": 1}}
    v = d.get("b")
    if v is None:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
