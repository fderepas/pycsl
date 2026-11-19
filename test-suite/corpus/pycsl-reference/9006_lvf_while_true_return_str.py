r"""Test 9006 -- lvF cap-return-exn-nonint (expected PASS): a `-> str` function whose body is a
`while True:` loop with no `break` and nothing after it; its only exits are the in-loop returns. The
loop block is ended by `absurd`, which is a proof obligation (the loop exit condition `not true` is
false), not an assumption; at base the block had type `unit` against the `string` result and the
inner int `Return` catch did not type-check. Twin: 9008 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations


#@ requires n >= 0
#@ ensures \result == s
#@ assigns \nothing
def drain(s: str, n: int) -> str:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while True:
        if i >= n:
            return s
        i = i + 1


if __name__ == "__main__":
    r = drain("ab", 3)
    print("VIOLATION contract" if r != "ab" else "result", r)
