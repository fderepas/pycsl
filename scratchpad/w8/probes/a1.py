#@ requires True
#@ ensures True
#@ assigns \nothing
def g(n: int) -> int:
    assert n > 0
    return n

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def driver() -> int:
    try:
        v: int = g(-1)
        return 1
    except AssertionError:
        return 2
