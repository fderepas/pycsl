r"""Test 6510 -- route #432 (expected FAIL): `n.next.v` with `next: Optional[Node]` (g4 probe) under `#@ no_exception \all`. Not PROVED at base 1c083dcbe either (refused: the erased field read flows into `-> int`); a RULE witness: #432 now refuses it first (an Optional field path is not narrowed). CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import Optional

class Node:
    def __init__(self, v: int) -> None:
        self.v: int = v
        self.next: Optional["Node"] = None


#@ no_exception \all
def f(n: Node) -> int:
    return n.next.v


if __name__ == "__main__":
    try:
        r = f(Node(1))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
