r"""Test 1315 — ROUTE #116 second carrier: `name = "inc" if c else "dec"; Pick(name)(3)` on a callable class was a class-by-name construction whose DECLINE returned the literal 0, so `\result == 0` PROVED (CPython 2). A decline is now `(any int)`. NOTE the string-literal arm of #116 (`Pick("inc")(3)` lowered as `(inc 3)`) is still OPEN.
"""
# pycsl-expected: FAIL
#@ ensures \result == y + 1
#@ assigns \nothing
def inc(y: int) -> int:
    return y + 1


class Pick:
    #@ assigns self.name
    def __init__(self, name: str) -> None:
        self.name = name

    #@ ensures \result == y - 1
    #@ assigns \nothing
    def __call__(self, y: int) -> int:
        return y - 1


#@ ensures \result == 0
#@ assigns \nothing
def f(c: bool) -> int:
    name = "inc" if c else "dec"
    return Pick(name)(3)
