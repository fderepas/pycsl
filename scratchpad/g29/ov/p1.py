r"""operator precedence not and or"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    a = False
    b = True
    return not a or b and False


if __name__ == "__main__":
    print("CPython:", probe())
