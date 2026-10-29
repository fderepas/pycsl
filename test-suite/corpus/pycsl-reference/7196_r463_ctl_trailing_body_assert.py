r"""Test 7196 -- route #463 (expected PASS): CONTROL -- an indented `#@ assert` that ends a body (the footer of the last statement of a suite) and a claim between a decorator and its def. Every `#@` line is attached; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class K:
    @staticmethod
    #@ ensures \result == n + 1
    def inc(n: int) -> int:
        return n + 1


#@ ensures \result == n
def f(n: int) -> int:
    x = n
    if x > 0:
        x = x + 0
        #@ assert x == n
    return x


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
