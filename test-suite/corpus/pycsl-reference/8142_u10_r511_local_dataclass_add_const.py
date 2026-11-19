r"""Test 8142 -- route #511 (expected FAIL: PROVED at base, REFUSED PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE): `K = 5`, then a local `@dataclass class K` and `return n + K` under `no_exception \all`; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


#@ no_exception \all
def f(n: int) -> int:
    @dataclass
    class K:
        v: int = 0
    return n + K


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 6):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
