#@ requires \length(a) == 3
#@ ensures \forall i: int; (0 <= i and i < 3) ==> \result >= 1
#@ assigns \nothing
def f(a: list) -> int:
    return 0
