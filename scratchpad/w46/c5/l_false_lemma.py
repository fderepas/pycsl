_ = 0  # anchor
#@ lemma
#@ requires True
#@ ensures 0 == 1
#@ assigns \nothing
def bogus() -> None:
    pass


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 0
