# Advice audit, route #460 NOTE, 'an obligation it owes is discharged by ITS OWN #@ requires': witness
# 7051's reached g given `#@ requires n > 0`, established by f. Expected: VERIFIES (= control 7054).


#@ requires n > 0
def g(n: int) -> int:
    assert n > 0
    return n


#@ requires n > 0
#@ no_exception \all
def f(n: int) -> int:
    return g(n)
