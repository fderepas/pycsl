r"""Test 1646 - ROUTE #182 carrier (gen #29): an uncontracted helper `shift(x)` returning `1 << x`, called with -1 under the caller's `#@ no_exception ValueError`, PROVED (CPython ValueError: negative shift count): the shift trigger is consulted only under the callee's own context.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def shift(x: int) -> int:
    return 1 << x


#@ no_exception ValueError
#@ ensures \result == 0
def probe() -> int:
    v = shift(-1)
    return 0
