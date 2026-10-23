r"""Test 2246 — route #241 (expected FAIL): a generator COMPARED directly lowered to `0 = 0`, so
the branch was decided and `\result == 1` PROVED at 1e4b380e while CPython `m()` = 0 (a
generator object is never equal to `0`). Now `(any int) = 0`; the postcondition is unproved.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    if (v for v in [1]) == 0:
        return 1
    return 0
