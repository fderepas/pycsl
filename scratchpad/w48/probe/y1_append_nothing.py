#@ requires True
#@ ensures True
#@ assigns \nothing
def g(a: list) -> None:
    a.append(1)

#@ requires \length(a) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(a: list) -> int:
    g(a)
    return len(a)
