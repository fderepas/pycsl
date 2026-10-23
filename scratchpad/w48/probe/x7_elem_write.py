#@ requires \length(a) > 0
#@ ensures True
#@ assigns a
def g(a: list) -> None:
    a[0] = 99

#@ requires \length(a) > 0 and a[0] == 1
#@ ensures \result == 1
#@ assigns a
def f(a: list) -> int:
    g(a)
    return a[0]
