#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    xs = [1, 2]
    for v in xs:
        pass
    else:
        #@ assert 1 == 2
        pass
    return 0
