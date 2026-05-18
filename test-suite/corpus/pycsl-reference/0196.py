"""Test 0196 — PyCSL Annotation Reference 4.4 (pure function as predicate in contract)"""
""  # pycsl
#@ requires lo <= hi
#@ ensures \result >= lo and \result <= hi
#@ assigns \nothing
def clamp(x: int, lo: int, hi: int) -> int:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x

#@ requires n >= 0
#@ ensures \result == clamp(x, 0, n)
#@ assigns \nothing
def clamp_positive(x: int, n: int) -> int:
    return clamp(x, 0, n)

if __name__ == "__main__":
    assert clamp_positive(-5, 10) == 0
    assert clamp_positive(7, 10) == 7
    assert clamp_positive(15, 10) == 10
