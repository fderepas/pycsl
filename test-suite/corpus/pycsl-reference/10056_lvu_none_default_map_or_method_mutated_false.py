r"""Test 10056 -- lvU none-default map parameter `x or {}` (expected FAIL): a METHOD mutates `d`
after `d = d or {}`. CPython mutates the caller's dict when it is non-empty (`m` gains "b"), so the
caller's claim `\result == 0` (that "b" is still absent) is false. A caller-visible mutation of a
dict parameter is refused (PYCSL-WHYML-PARAM-COLLECTION-MUT) or the arm is closed; it must never
model the write as local to the callee. Control: 10050.
"""
# pycsl-expected: FAIL
from typing import Dict, Optional


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.k: int = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def put(self, d: Optional[Dict[str, int]] = None) -> int:
        d = d or {}
        d["b"] = 1
        return 0

    #@ ensures \result == 0
    #@ assigns \nothing
    def caller(self) -> int:
        m: Dict[str, int] = {}
        m["a"] = 1
        self.put(m)
        if "b" in m:
            return 1
        return 0


if __name__ == "__main__":
    r = C().caller()
    print("VIOLATION contract" if r != 0 else "result", r)
