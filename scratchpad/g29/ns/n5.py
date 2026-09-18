r"""None dict value"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    d: Dict[str, Optional[int]] = {"a": None}
    return d["a"] == 0


if __name__ == "__main__":
    print("CPython:", probe())
