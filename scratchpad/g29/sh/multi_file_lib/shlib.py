"""helper: a function named `val` returning 100."""


#@ ensures \result == 100
#@ assigns \nothing
def val() -> int:
    return 100
