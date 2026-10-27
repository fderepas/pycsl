r"""Test 6025 -- gen #37 route #408 (expected PASS): CONTROL: a module list never stored to, its element hashed (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
XS = [1, 2]


#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    s = {XS[0]}
    return 1


if __name__ == "__main__":
    print(f(), len(XS))
