r"""get missing key dict of floats"""
from typing import Dict, List, Set, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    d: Dict[str, float] = {"a": 1.0}
    return d.get("b") == 0.0


if __name__ == "__main__":
    print("CPython:", probe())
