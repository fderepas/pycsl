# Route #523 advice probe: witness g1016_x1076 with the appended element folded into the
# literal ("bind the final list as one literal"; here "xyz" instead of "z", which keeps the
# claim honest). CPython returns 0; expected: VERIFIES `\result == 0`.
from typing import Any, Dict, List, Optional


#@ ensures \result == 0
def f(k: int) -> int:
    a = ["abc", "defg", "xyz"]
    for p in a:
        if p == "z":
            return 1
    return 0


if __name__ == "__main__":
    print("result", f(0))
