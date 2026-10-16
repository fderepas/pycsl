r"""Test 2342 — route #247 (expected FAIL): `set` and `frozenset` shared one tag, so a subject declared
`set` decided `isinstance(x, frozenset)` TRUE; `\result == 1` PROVED at afe28c69. CPython `f({1})` = 0
(`class X(set, frozenset)` is a layout-conflict TypeError, so no value is both).
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
def f(x: set) -> int:
    if isinstance(x, frozenset):
        return 1
    return 0


if __name__ == "__main__":
    assert f({1}) == 0
