r"""Test 3924 -- gen #37 route #307 (expected PASS): CONTROL: `(x := 5) + x` proves the CPython value 10.
"""
# pycsl-expected: PASS
#@ ensures \result == 10
def f() -> int:
    x = 0
    y = (x := 5) + x
    return y

if __name__ == "__main__":
    assert f() == 10
