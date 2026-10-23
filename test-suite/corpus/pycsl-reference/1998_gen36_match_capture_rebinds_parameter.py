r"""Test 1998 — gen #36 (expected PASS): ROUTE #233 — a capture rebinds a parameter

`match 7: case k:` rebinds the parameter `k` (route #153's shape); after the `match` `k` is 7
whatever the argument, as in CPython.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == 7
#@ assigns \nothing
def f(k: int) -> int:
    match 7:
        case k:
            pass
    return k
