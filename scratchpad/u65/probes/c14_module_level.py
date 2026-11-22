#@ \abstract
#@ ensures \result != 3
def oracle(x: int) -> int:
    return 0

X = oracle(3)
assert X == 77

#@ ensures \result == 1
def f(y: int) -> int:
    return 1
