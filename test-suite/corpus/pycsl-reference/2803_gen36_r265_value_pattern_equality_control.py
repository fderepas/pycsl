r"""Test 2803 — route #265 CONTROL (expected PASS): `case 0:` / `case 1:` are VALUE patterns and
compare by EQUALITY (PEP 634), which the model keeps. CPython `f(0), f(1), f(2)` = 7, 1, 0.
"""
# pycsl-expected: PASS
#@ ensures n == 0 ==> \result == 7
#@ ensures n == 1 ==> \result == 1
#@ assigns \nothing
def f(n: int) -> int:
    match n:
        case 0:
            return 7
        case 1:
            return 1
        case _:
            return 0

if __name__ == "__main__":
    print(f(0), f(1), f(2))
