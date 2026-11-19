r"""Test 9009 -- lvF cap-return-exn-nonint (expected PASS): a `-> None` procedure whose `while` loop
holds a bare `return`. The in-loop return raises `Return_void`, caught by the function-level wrap; at
base the while arm's inner `with Return r -> r` catch named the undeclared int `Return` exception and
the file failed L3-tc. Nothing about the loop is assumed: the postcondition is the frame alone.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List


#@ requires n >= 0 and len(xs) >= n
#@ ensures len(xs) >= n
#@ assigns \nothing
def scan(xs: List[int], n: int) -> None:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if xs[i] == 0:
            return
        i = i + 1


if __name__ == "__main__":
    scan([1, 0, 2], 3)
    print("result", "ok")
