r"""None stored into a dict by key"""
from typing import List, Dict, Optional, Set, Tuple
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    d: Dict[str, Optional[int]] = {}
    d["a"] = None
    return d["a"] == 0


if __name__ == "__main__":
    print("CPython:", probe())
