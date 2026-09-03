#@ requires True
class C(
#@ class invariant 1 == 2
        object):
    pass

#@ ensures \result == 2
def g() -> int:
    return 2
