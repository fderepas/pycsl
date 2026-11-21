r"""Test 4514 -- gen #37 route #336 (expected FAIL): plain alias `N2 = float | None`: the arm was `int`, `x % 1 == 0` PROVED; CPython False for 0.5. Resolved to `float | None`; not provable.
"""
# pycsl-expected: FAIL
N2 = float | None
#@ ensures \result == True
def f(x: N2) -> bool:
    if x is None:
        return True
    return x % 1 == 0
if __name__ == "__main__":
    assert f(0.5) == True
