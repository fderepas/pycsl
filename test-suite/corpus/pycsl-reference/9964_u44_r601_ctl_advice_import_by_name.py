r"""Test 9964 -- route #601 advice control (expected PASS): rt58 d07 with the advice of PYCSL-R601-HANDLER-TUPLE-NON-NAME followed -- the class is imported by name (`from builtins import ValueError`) and the tuple holds bare names, so the raised ValueError is caught in the model; the claim separates the handler path (7) from the normal one (2)
"""
# pycsl-expected: PASS
from __future__ import annotations
from builtins import ValueError


#@ ensures (n > 0 and \result == 7) or (n <= 0 and \result == 2)
#@ assigns \nothing
def f(n: int) -> int:
    x = 0
    try:
        if n > 0:
            raise ValueError("v")
        x = 2
    except (ZeroDivisionError, ValueError):
        x = 7
    return x + 0 * n


if __name__ == "__main__":
    ok = f(1) == 7 and f(0) == 2
    print("result" if ok else "VIOLATION contract", f(1), f(0))
