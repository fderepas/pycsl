r"""Test 2703 — route #259 (expected FAIL): `2 ** -1` (literal operands) — the negative
exponent is a `UnaryOp`, so it reached `py_pow 2 (- 1)`, an int, and `x % 1 == 0` PROVED at
b35d9c5e. CPython: `0.5 % 1 == 0.5`, f() is False. Now owes the exponent obligation (and a
negative literal exponent is never constant-folded).
"""
# pycsl-expected: FAIL


#@ ensures \result == True
#@ assigns \nothing
def f() -> bool:
    x = 2 ** -1
    return x % 1 == 0


if __name__ == "__main__":
    assert f() is False
