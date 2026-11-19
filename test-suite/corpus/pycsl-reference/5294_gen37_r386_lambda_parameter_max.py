r"""Test 5294 -- gen #37 route #386 (expected FAIL): `g = lambda max: max(1, 2)` then `g(min) == 2`; PROVED at base (CPython 1). REFUSED (lambda parameter named like a builtin, route #386).
"""
# pycsl-expected: FAIL
#@ ensures \result == 2
#@ assigns \nothing
def m() -> int:
    g = lambda max: max(1, 2)
    return g(min)


if __name__ == "__main__":
    r = m()
    print("VIOLATION m() =", r) if r != 2 else print("no violation")
