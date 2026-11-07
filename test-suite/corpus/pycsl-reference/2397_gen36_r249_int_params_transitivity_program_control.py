r"""Test 2397 — route #249 (expected PASS): CONTROL: `int` transitivity still decides a program test: `requires x == y and y == z` PROVES
`if x == z: return 1` gives `\result == 1`.
"""
# pycsl-expected: PASS
#@ requires x == y and y == z
#@ ensures \result == 1
#@ assigns \nothing
def f(x: int, y: int, z: int) -> int:
    if x == z:
        return 1
    return 0


if __name__ == "__main__":
    assert f(4, 4, 4) == 1
