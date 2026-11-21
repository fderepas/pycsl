# Advice probe for PYCSL-R349-UNDERIVABLE-HASH-UNDER-CLAIM: witness 6470 with the claim dropped.
# Expected: VERIFIES (control 6480 is the same).
from typing import Dict, Any


#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1


if __name__ == "__main__":
    print(f({"a": "x"}))
