r"""Test 9148 -- lvD3 control (expected FAIL, refused before and after by R543): a single-part
f-string is the value-keyed `str_of_int_hash` in the int joiner, so it is excluded from the kept positions;
here the annotated rebinding is refused upstream.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ requires x == 1824800645
#@ ensures \result == True
#@ assigns \nothing
def f(x: int) -> bool:
    name: int = x
    name = "abc"  # type: ignore
    return f"{name}" == f"{x}"


if __name__ == "__main__":
    r = f(1824800645)
    print("VIOLATION contract" if r is not True else "result", r)
