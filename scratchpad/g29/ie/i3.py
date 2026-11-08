r"""implicit ZeroDivisionError caught by Exception"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    z = 0
    try:
        v = 10 // z
    except Exception:
        return 9
    return v

if __name__ == "__main__":
    print("CPython:", probe())
