r"""Test 6017 -- gen #37 route #404 (expected FAIL): route #380 coverage after #404 -- S1 now refuses every file metaclass that defines anything, so #380's `__call__` refusal is reached through an admitted stdlib metaclass: `C(1)` of `class C(enum.Enum, metaclass=enum.EnumMeta)` is a member LOOKUP (CPython `C.A`), not a construction. REFUSED at base and candidate (PYCSL-R380-METACLASS-CALL).
"""
# pycsl-expected: FAIL
import enum


class C(enum.Enum, metaclass=enum.EnumMeta):
    A = 1
    B = 2


#@ ensures \result == 1
def f() -> int:
    c = C(1)
    return 1


if __name__ == "__main__":
    print(f(), C(1))
