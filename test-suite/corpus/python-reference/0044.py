"""Test 0044 — Python Reference 3.2.4.3: numbers.Complex (complex).

REFUSED since relaunch #46 (route #43). `_py_expr_constant` lowered a complex
literal to `int(value.real)` — imaginary part DISCARDED, real part TRUNCATED — and
the resulting ordinary integer was DECIDABLE: `x = 3j; if x == 0:` proved the branch
Python does not take, and `if x:` proved the branch Python DOES take is not taken
(witnesses `pycsl-reference/1050`-`1052`).

This driver used to PASS because its own `\\result == 0` is true of the program for
reasons unrelated to the complex arithmetic: both `assert`s are DROPPED by Module 6
and the function returns 0 regardless. It passed WITHOUT the construct it exists to
exercise being modelled — the `python-reference/0209` lesson again.

PyCSL models no complex arithmetic; `c.real` / `c.imag` are not modelled either.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
def test_numbers_complex() -> int:
    """Complex numbers have real and imag parts."""
    c = 3 + 4j
    assert c.real == 3.0
    assert c.imag == 4.0
    return 0

if __name__ == "__main__":
    assert test_numbers_complex() == 0
