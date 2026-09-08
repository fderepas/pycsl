#@ requires True
#@ ensures True
#@ assigns a
def g(a: list) -> None:
    a.append(1)

#@ requires \length(a) == 0
#@ ensures \result == 0
#@ assigns a
def f(a: list) -> int:
    g(a)
    return len(a)
