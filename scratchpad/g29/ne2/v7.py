r"""float modulo zero"""
import math
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 0
def probe() -> int:
    f = 1.0 % 0.0
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
