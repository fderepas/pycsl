r"""Test 2460 — route #251 (expected PASS): CONTROL: builtin `int` parameters keep Why3 integer arithmetic and order:
commutativity, `x * 0`, `x % 1` and `<`-asymmetry still PROVE (true in CPython for every int).
"""
# pycsl-expected: PASS
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int, y: int) -> int:
    if x < y and y < x:
        return 1
    return (x + y) - (y + x) + x * 0 + x % 1 + (x - x)


if __name__ == "__main__":
    for x in range(-3, 4):
        for y in range(-3, 4):
            assert f(x, y) == 0
