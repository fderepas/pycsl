#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def driver() -> int:
    try:
        assert 1 == 2
        return 1
    except AssertionError:
        return 2
