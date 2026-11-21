r"""Test 4114 -- gen #37 route #318 (expected FAIL): `for i in range(o.n): o.n = 5` with a source variant re-read the field stop each iteration; `\result == 5` PROVED (CPython 2). Stop captured once.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.n = 2

#@ ensures \result == 5
def f() -> int:
    o = C()
    c = 0
    #@ loop invariant 0 <= i <= 5
    #@ loop invariant c == i
    #@ loop invariant c == 0 ==> o.n == 2
    #@ loop invariant c > 0 ==> o.n == 5
    #@ loop variant 6 - i
    for i in range(o.n):
        o.n = 5
        c += 1
    return c

if __name__ == "__main__":
    assert f() == 5, f()
