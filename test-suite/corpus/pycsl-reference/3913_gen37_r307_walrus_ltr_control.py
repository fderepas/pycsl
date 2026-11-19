r"""Test 3913 -- gen #37 route #307 (expected PASS): CONTROL: the walrus witness with the CPython value: `x - (x := 1) + 1` proves `\result == 0`.
"""
# pycsl-expected: PASS
#@ ensures \result == 0
def f() -> int:
    x = 0
    return x - (x := 1) + 1

if __name__ == "__main__":
    assert f() == 0
