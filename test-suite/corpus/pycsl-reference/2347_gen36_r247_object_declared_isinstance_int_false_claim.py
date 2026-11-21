r"""Test 2347 — route #247 (expected FAIL): a subject declared `object` took `tag_object` as its OWN tag
and decided `isinstance(x, int)` FALSE (`(99 = 0)`); `\result == 0` PROVED at afe28c69. CPython `f(5)` = 1.
"""
# pycsl-expected: FAIL


#@ ensures \result == 0
#@ assigns \nothing
def f(x: object) -> int:
    if isinstance(x, int):
        return 1
    return 0


if __name__ == "__main__":
    assert f(5) == 1
