# pycsl-expected: FAIL
"""1287 - (#49) ROUTE #100 REFERENCE ARM: the FREE-FUNCTION spelling, which was correct all
along.

Byte-for-byte the same contracts and bodies as 1285 with the class removed. It was REFUSED
before the repair and is REFUSED after it. Its whole job is to hold the reference behaviour
in place: route #100 was found by noticing that this file and 1285 disagree, and if the
method path ever diverges from this one again, the pair says so.
"""
_ = 0  # anchor
#@ requires 1 == 1
#@ ensures \result >= 0
#@ raises ValueError when n < 0
def checked_abs(n: int) -> int:
    if n < 0:
        raise ValueError
    return n


#@ requires 1 == 1
#@ no_exception ValueError
#@ assigns \nothing
def caller(k: int) -> int:
    return checked_abs(k)
