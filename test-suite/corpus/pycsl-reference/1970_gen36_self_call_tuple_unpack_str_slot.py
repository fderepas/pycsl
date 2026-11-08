r"""Test 1970 — gen #36 (expected PASS): a `self.<m>(...)` call whose callee returns a
`Tuple[List[str], int]` (a seq-promoted `List[str]` local + the loop index), UNPACKED at two
call sites of one caller. Four links of the abstract self-call stub, each an L3-tc error at
base: the tuple-unpack handler DOWNGRADED the stub's declared `(array string, int)` return to
`(int, int)` (the second call site then got a route-#188 twin); the `array string` unpack
target was pre-declared `ref 0`; the stub's `List[str]` formal was `array int`; and the
callee precondition `n <= len(raw)` asserted at the call (route #167) used the opaque
`iter_length : int -> int` on the array actual. The callee's `\result[1] == n` now reaches the
stub as a tuple projection, so the caller proves `a + b == n + n`. Twin: 1971 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List, Tuple


class Folder:
    #@ requires 0 <= n and n <= len(raw)
    #@ ensures \result[1] == n
    #@ assigns \nothing
    def collect(self, raw: List[str], n: int) -> Tuple[List[str], int]:
        out: List[str] = []
        i = 0
        #@ loop invariant 0 <= i and i <= n
        #@ loop variant n - i
        while i < n:
            out.append(raw[i].strip())
            i += 1
        return out, i

    #@ requires 0 <= n and n <= len(raw)
    #@ ensures \result == n + n
    #@ assigns \nothing
    def twice(self, raw: List[str], n: int) -> int:
        first, a = self.collect(raw, n)
        second, b = self.collect(raw, n)
        return a + b
