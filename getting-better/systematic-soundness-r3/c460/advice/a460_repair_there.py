# Advice audit, route #460 NOTE, 'the repair above applies THERE': witness 7050's #161 repair ("give the
# callee a contract") applied in the reached g -- the library call replaced by a verified program function
# with a contract, g guarded by its own requires. Expected: VERIFIES under f's `#@ no_exception \all`.

#@ requires n >= 0
#@ ensures \result >= 1
def fact(n: int) -> int:
    r = 1
    i = 1
    #@ loop invariant 1 <= i and i <= n + 1
    #@ loop invariant r >= 1
    #@ loop variant n + 1 - i
    while i <= n:
        r = r * i
        i = i + 1
    return r


#@ requires n >= 0
def g(n: int) -> int:
    return fact(n)


#@ requires n >= 0
#@ no_exception \all
def f(n: int) -> int:
    return g(n)
