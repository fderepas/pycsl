r"""Test 5061 -- gen #37 route #374 (expected FAIL): external `a.__x = 5` on a slotted A with slots `__x`, `y`; PROVED at base (AttributeError). REFUSED now.
"""
# pycsl-expected: FAIL
class A:
    __slots__ = ("__x", "y")
    def __init__(self) -> None:
        self.__x = 1
        self.y = 0

#@ no_exception \all
def f(a: A) -> int:
    a.__x = 5
    return a.y

if __name__ == "__main__":
    print(f(A()))
