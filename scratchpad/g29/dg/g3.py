r"""get of missing key in dict of lists, len"""
from typing import Dict, List, Set, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, List[int]] = {"a": [1]}
    v = d.get("b")
    return len(v)


if __name__ == "__main__":
    print("CPython:", probe())
