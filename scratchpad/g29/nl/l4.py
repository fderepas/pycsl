r"""None string local"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    s: Optional[str] = None
    return s == ""


if __name__ == "__main__":
    print("CPython:", probe())
