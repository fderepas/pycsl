r"""Test 9005 -- lvF cap-return-exn-nonint (expected PASS): a `-> str` function whose `while` loop
holds a `return`. The in-loop return raises the typed `Return_str`, caught by the function-level wrap.
At base the `while` arm ALSO wrapped the loop in a catch of the int-payload `Return` (`with Return r ->
r`), which cannot type-check in a string function (the exception is not even declared there), so the
file failed L3-tc. The for-loop arm already omitted that inner catch whenever the function-level wrap
exists; the while arm now does the same for every non-int return type.
Twins: 9007 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations


#@ requires n >= 0
#@ ensures \result == "x" or \result == s
#@ assigns \nothing
def first_hit(s: str, n: int) -> str:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if i == 3:
            return "x"
        i = i + 1
    return s


if __name__ == "__main__":
    r = first_hit("ab", 5)
    print("VIOLATION contract" if r != "x" else "result", r)
