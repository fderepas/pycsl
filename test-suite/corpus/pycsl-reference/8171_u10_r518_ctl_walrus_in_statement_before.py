r"""Test 8171 -- route #518 (control, expected PASS): the binding moved to a statement of its own (`T = 0`) and the lambda default reads the plain name, as the refusal advises; K untouched; CPython returns 5
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5
T = 0
_l = lambda a=T: a


#@ ensures \result == 5
def f() -> int:
    return K


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
