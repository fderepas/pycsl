r"""Test 8162 -- route #518 (expected FAIL: PROVED at base, REFUSED PYCSL-R518-WALRUS-AT-DEFINITION-TIME): a lambda inside a list display whose default rebinds K; `K == 5` claimed True; CPython False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

K = 5


#@ ensures \result == True
def f() -> bool:
    return K == 5


_ls = [lambda a=(K := 0): a]


if __name__ == "__main__":
    try:
        r = f()
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
