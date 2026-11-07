r"""None dict value len"""
from typing import List, Dict, Optional, Tuple
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    d: Dict[str, Optional[str]] = {"a": None}
    s = d["a"]
    return len(s)


if __name__ == "__main__":
    print("CPython:", probe())
