"""Helper for corpus 7286 (route #467 control): a callee claiming `no_exception \\all`."""


#@ no_exception \all
#@ requires x >= 0
#@ ensures \result == x
def g(x: int) -> int:
    assert x >= 0
    return x
