r"""Test 5296 -- gen #37 route #386 (expected FAIL): function-local `from operator import sub as max`, `max(3, 1) == 3`; PROVED at base (CPython 2). REFUSED (route #386).
"""
# pycsl-expected: FAIL
#@ ensures \result == 3
#@ assigns \nothing
def m() -> int:
    from operator import sub as max
    return max(3, 1)


if __name__ == "__main__":
    r = m()
    print("VIOLATION m() =", r) if r != 3 else print("no violation")
