"""Test 0194 — PyCSL Annotation Reference 4.4 (pure function call in contract)"""
""  # pycsl
#@ ensures \result >= 0
#@ assigns \nothing
def abs_val(x: int) -> int:
    if x >= 0:
        return x
    return -x

#@ ensures \result == abs_val(a) + abs_val(b)
#@ assigns \nothing
def sum_abs(a: int, b: int) -> int:
    return abs_val(a) + abs_val(b)

if __name__ == "__main__":
    assert sum_abs(3, -4) == 7
    assert sum_abs(-1, -2) == 3
