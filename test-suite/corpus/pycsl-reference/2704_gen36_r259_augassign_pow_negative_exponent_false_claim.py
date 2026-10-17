r"""Test 2704 — route #259 (expected FAIL): `x **= n` with `n < 0` went through the
augmented-assignment twin (`val py_pow`, unguarded), so `x % 1 == 0` PROVED at b35d9c5e.
CPython: f(-1) is False. Now the SAME guarded declaration as the `**` expression site.
"""
# pycsl-expected: FAIL


#@ requires n < 0
#@ ensures \result == True
#@ assigns \nothing
def f(n: int) -> bool:
    x = 2
    x **= n
    return x % 1 == 0


if __name__ == "__main__":
    assert f(-1) is False
