"""Test 0297 — PyCSL Annotation Reference 7.6 — Ghost tuple variables"""
_ = 0  # anchor

#@ requires a >= 0 and b >= 0
#@ ensures \result == a + b
#@ assigns \nothing
def sum_pair(a: int, b: int) -> int:
    #@ ghost p : tuple2 = \mktuple(a, b)
    return a + b


#@ requires a >= 0 and b >= 0 and c >= 0
#@ ensures \result == a + b + c
#@ assigns \nothing
def sum_triple(a: int, b: int, c: int) -> int:
    #@ ghost t : tuple3 = \mktuple(a, b, c)
    return a + b + c


if __name__ == "__main__":
    assert sum_pair(2, 3) == 5
    assert sum_pair(0, 0) == 0
    assert sum_triple(1, 2, 3) == 6
    print("PASS")
