r"""Test 5156 -- gen #37 route #380 (expected FAIL): a metaclass `__call__` returning 42 while `C(1).x == 1` PROVED (CPython AttributeError). PROVED at base b815ee8d8.
"""
# pycsl-expected: FAIL
class M(type):
    def __call__(cls, *args: int) -> int:
        return 42

class C(metaclass=M):
    def __init__(self, x: int) -> None:
        self.x = x

#@ ensures \result == 1
def f() -> int:
    c = C(1)
    return c.x

if __name__ == "__main__":
    print(f())
