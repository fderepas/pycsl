r"""None local read as zero (route 56 core)"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    x: Optional[int] = None
    return x == 0


if __name__ == "__main__":
    print("CPython:", probe())
