r"""Test 1358 — ROUTE #122 (nested arm): `a()` and `b()` each define a helper `h` (+1 / -1); the lift emitted ONE `h` (b's) and `a()` PROVED `\result == 2` while CPython returns 4. A lifted helper whose name another function shares is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 2
#@ assigns \nothing
def a() -> int:
    def h(y: int) -> int:
        return y + 1
    return h(3)


#@ assigns \nothing
def b() -> int:
    def h(y: int) -> int:
        return y - 1
    return h(3)
