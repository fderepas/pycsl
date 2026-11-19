r"""Test 6873 -- route #457 (expected PASS): CONTROL -- `isinstance` with an imported name resolving to a real class (`from fractions import Fraction`) inside a tuple with a builtin class. Not refused by PYCSL-R457-CLASS-SPEC-NOT-A-CLASS.
"""
# pycsl-expected: PASS
from fractions import Fraction


#@ no_exception \all
def f(x: int) -> int:
    if isinstance(x, (Fraction, str)):
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(1))
