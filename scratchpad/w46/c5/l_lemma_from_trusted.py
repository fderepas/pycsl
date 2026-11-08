_ = 0  # anchor
#@ \trusted
#@ ensures \result == 1
#@ assigns \nothing
def t() -> int:
    return 0


#@ lemma
#@ requires True
#@ ensures t() == 1
#@ assigns \nothing
def lem() -> None:
    pass


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return 0
