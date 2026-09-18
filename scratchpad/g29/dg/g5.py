r"""get missing key dict of bools"""
from typing import Dict, List, Set, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    d: Dict[str, bool] = {"a": True}
    return d.get("b") == False


if __name__ == "__main__":
    print("CPython:", probe())
