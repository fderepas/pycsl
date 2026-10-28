r"""Test 6513 -- route #432 (expected FAIL): a call between an attribute-path guard and the use (g4 probe) under `#@ no_exception \all`. Not PROVED at base 1c083dcbe either (refused: the erased field read flows into `-> int`); a RULE witness for the narrowing STOP at a call between an attribute-path guard and the use. CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional

class Node:
    def __init__(self) -> None:
        self.nxt: Optional["Node"] = None
        self.v: int = 0

    def clear(self) -> None:
        self.nxt = None


#@ no_exception \all
def f(n: Node) -> int:
    if n.nxt is not None:
        n.clear()
        return n.nxt.v
    return 0


if __name__ == "__main__":
    m = Node()
    m.nxt = Node()
    try:
        r = f(m)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
