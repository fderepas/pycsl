# Advice probe for PYCSL-R430: witness 6460 with `\all` dropped from the caller's claim. Expected:
# VERIFIES (the TypeError is ambient for both functions: an abnormal exit only, since route #431).
from typing import Dict, Any


#@ ensures \result == 1
def h(m: Dict[str, Any]) -> int:
    s = {m.get("a")}
    return 1


#@ ensures \result == 1
def caller(m: Dict[str, Any]) -> int:
    return h(m)


if __name__ == "__main__":
    print(caller({"a": "x"}))
