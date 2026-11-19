r"""Test 2341 — route #247 (expected FAIL): the converse of 2340. A subject declared `set` decided
`isinstance(x, dict)` TRUE through the shared tag; `\result == 1` PROVED at afe28c69. CPython
`f({1})` = 0.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
def f(x: set) -> int:
    if isinstance(x, dict):
        return 1
    return 0


if __name__ == "__main__":
    assert f({1}) == 0
