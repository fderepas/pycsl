r"""Test 2461 — route #251 (expected PASS): CONTROL: on an `int` parameter, `-x` is integer negation: `if x: if not -x:
return 1` is unreachable and `\result == 0` still PROVES (true in CPython for every int).
"""
# pycsl-expected: PASS
#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    if x:
        if not -x:
            return 1
    return 0


if __name__ == "__main__":
    for x in range(-5, 6):
        assert f(x) == 0
