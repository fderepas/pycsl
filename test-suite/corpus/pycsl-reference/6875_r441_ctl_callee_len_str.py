r"""Test 6875 -- routes #441 / #444-#458 callee reach (expected PASS): CONTROL -- the unclaimed callee's `len(s)` takes a `str`, which #441's row admits under the caller's claim.
"""
# pycsl-expected: PASS


def g(s: str) -> int:
    return len(s)


#@ no_exception \all
def f(s: str) -> int:
    return g(s)


if __name__ == "__main__":
    print("result", f("ab"))
