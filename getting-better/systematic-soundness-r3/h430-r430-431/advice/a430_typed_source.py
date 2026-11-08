# Advice probe for PYCSL-R430: witness 6460 with the callee's hashed value declared with a hashable
# type at its source (`m: Dict[str, str]` instead of `Dict[str, Any]`). Expected: VERIFIES.
from typing import Dict


#@ ensures \result == 1
def h(m: Dict[str, str]) -> int:
    s = {m.get("a")}
    return 1


#@ no_exception \all
#@ ensures \result == 1
def caller(m: Dict[str, str]) -> int:
    return h(m)


if __name__ == "__main__":
    print(caller({"a": "x"}))
