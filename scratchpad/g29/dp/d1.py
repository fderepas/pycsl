r"""deep import chain constant"""
from typing import List, Dict, Optional
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
