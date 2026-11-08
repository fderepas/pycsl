r"""Test 9172 -- route #571 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R571-ENUM-MEMBER-NAME-KIND; a new false proof beyond red team 54's family, measured PROVED at base 8358d5d31): `return E.A.name + 1`; CPython TypeError: can only concatenate str (not "int") to str
"""
# pycsl-expected: FAIL
import enum
from typing import Dict
class E(enum.Enum):
    A = 1
class SE(enum.StrEnum):
    S = "ab"
class FL(enum.IntFlag):
    R = 1

#@ no_exception \all
def f(k: int) -> int:
    return E.A.name + 1

if __name__ == "__main__":
    print(f(1))
