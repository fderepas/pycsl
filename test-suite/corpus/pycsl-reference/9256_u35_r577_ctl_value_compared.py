r"""Test 9256 -- route #577 CONTROL (expected PASS at base and HEAD) and the advice of PYCSL-R577-ENUM-MEMBER-VALUE-OPERAND /
the extended PYCSL-R571-ENUM-MEMBER-NAME-KIND: a member's `.value` / `.name` compared with `==` / `!=` is admitted for a plain
Enum, an IntFlag, a member bound to a module constant and a class attribute (`k == EE.A.value`, `MA.name == "A"`).
"""
# pycsl-expected: PASS
import enum


class EE(enum.Enum):
    A = 1
    B = 2


class FL(enum.IntFlag):
    R = 1
    W = 2


MA = EE.A


class H:
    m = EE.B


#@ no_exception \all
def f1(k: int) -> int:
    return 1 if k == EE.A.value else 0


#@ no_exception \all
def f2(k: int) -> int:
    return 1 if k != FL.R.value else 0


#@ no_exception \all
def f3(k: int) -> int:
    return 1 if MA.name == "A" else 0


#@ no_exception \all
def f4(k: int) -> int:
    return 1 if H.m.value == k else 0


if __name__ == "__main__":
    print(f1(1), f2(1), f3(1), f4(2))
