r"""Test 9965 -- route #602 advice control (expected PASS): rt58 d08 with the advice of PYCSL-R602-HANDLER-NAME-REBOUND followed -- the handler names the exception class itself (`except ValueError:`), so the raised ValueError is caught in the model; the claim separates the handler path (1) from the normal one (0)
"""
# pycsl-expected: PASS
from __future__ import annotations


#@ ensures (n > 0 and \result == 1) or (n <= 0 and \result == 0)
#@ assigns \nothing
def f(n: int) -> int:
    x = 0
    try:
        if n > 0:
            raise ValueError("v")
        x = 0
    except ValueError:
        x = 1
    return x


if __name__ == "__main__":
    ok = f(1) == 1 and f(0) == 0
    print("result" if ok else "VIOLATION contract", f(1), f(0))
