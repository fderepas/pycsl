r"""Test 8920 -- lvD f-string ternary segment (expected PASS): in a `-> str` function, an interpolated
ternary whose BOTH arms are strings (`f"x{'a' if c else 'b'}"`) is a Python `str`, so it lowers to the
exact Why3 `(if c then "a" else "b")` segment of the `str_concat_op` chain. At base the segment was
`int_to_string (<string>)`, a Why3 type error. Twins: 8921, 8922 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations


#@ requires c == True
#@ ensures \result == "xa"
#@ assigns \nothing
def tag(c: bool) -> str:
    return f"x{'a' if c else 'b'}"


if __name__ == "__main__":
    r = tag(True)
    print("VIOLATION contract" if r != "xa" else "result", r)
