r"""sys.exit"""
from typing import List, Dict
_ = 0  # anchor


import sys


#@ ensures \result == 5
def probe() -> int:
    sys.exit(1)


if __name__ == "__main__":
    print("CPython:", probe())
