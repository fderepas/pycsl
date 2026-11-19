# Advice probe for PYCSL-R431: witness 6450 with the `return` MOVED AFTER the `try` statement, as
# the message says. The ambient TypeError now propagates (abnormal exit), and the ensures holds of
# every NORMAL return: expected VERIFIES.
from typing import Dict, Any, List


#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(m: Dict[str, Any], out: List[int]) -> None:
    out[0] = 2
    try:
        n = hash(m.get("a"))
        out[0] = 1
    finally:
        pass
    return


if __name__ == "__main__":
    o = [0]
    try:
        f({"a": [1]}, o)
    except TypeError:
        print("TypeError (abnormal exit, no normal return)")
