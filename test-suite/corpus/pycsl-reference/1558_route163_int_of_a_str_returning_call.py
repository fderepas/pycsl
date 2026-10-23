r"""Test 1558 - ROUTE #163 (gen #29, carrier of route #66): `int(getname())` with `getname() -> str` returning "x"; #66 recognised a string only as a literal or a `str`-typed name, so `no_exception ValueError` PROVED; CPython raises. The argument must now be provably numeric.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ assigns \nothing
def getname() -> str:
    return "x"


#@ no_exception ValueError
def probe() -> int:
    return int(getname())

