r"""Test 1694 - ROUTE #198 control (gen #30): the repair touches ONLY the bare `return`. A genuine early return of a genuine value still carries that value through the same `raise (Return ...)` path and still proves. Without this control the #198 fix could have been the blunt one - turning every early return opaque - and the corpus would not have noticed.
"""

_ = 0  # anchor


#@ requires x > 0
#@ ensures \result == 3
def f(x: int) -> int:
    if x > 0:
        return 3
    return 5
