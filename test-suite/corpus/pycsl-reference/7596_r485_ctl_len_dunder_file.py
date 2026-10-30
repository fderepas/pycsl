r"""Test 7596 -- route #485 control (expected PASS): `len(__file__) >= 0` -- `len` of the str `__file__` is a documented int (route #325's known-int call), so the origin rule does not touch it.
"""
# pycsl-expected: PASS


#@ ensures \result >= 0
def f(n: int) -> int:
    return len(__file__) * 0


if __name__ == "__main__":
    print("result", f(1))
