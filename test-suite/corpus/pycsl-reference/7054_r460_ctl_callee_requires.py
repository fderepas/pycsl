r"""Test 7054 -- route #460 (expected PASS): CONTROL -- the un-claimed `g`'s `assert n > 0` is discharged by g's own `#@ requires n > 0`, which the claiming `f` establishes; PROVED at base and candidate.
"""
# pycsl-expected: PASS


#@ requires n > 0
def g(n: int) -> int:
    assert n > 0
    return n


#@ requires n > 0
#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    print(f(3))
