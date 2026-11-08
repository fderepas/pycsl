r"""del dict key then membership"""
from typing import List, Dict
_ = 0  # anchor


#@ ensures \result == True
def probe() -> bool:
    d: Dict[str, int] = {"a": 1}
    del d["a"]
    return "a" in d


if __name__ == "__main__":
    print("CPython:", probe())
