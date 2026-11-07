r"""get missing key in dict of strings compared to empty"""
from typing import Dict, List, Set, Optional
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    d: Dict[str, str] = {"a": "x"}
    return d.get("b") == ""


if __name__ == "__main__":
    print("CPython:", probe())
