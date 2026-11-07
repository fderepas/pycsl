r"""for tuple target over strings"""
from typing import List, Dict, Tuple
_ = 0  # anchor


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    words: List[str] = ["abc"]
    for a, b in words:
        pass
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
