r"""Test 5171 -- gen #37 route #380 (expected PASS): CONTROL: a metaclass that binds no `__call__`: `C(1).x == 1` (CPython ok).
"""
# pycsl-expected: PASS
class M(type):
    pass

class C(metaclass=M):
    def __init__(self, x: int) -> None:
        self.x = x

#@ ensures \result == 1
def f() -> int:
    c = C(1)
    return c.x

if __name__ == "__main__":
    print(f())
