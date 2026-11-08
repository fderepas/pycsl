r"""Test 6871 -- route #445 (expected PASS): CONTROL -- a field assigned on every `__init__` path (the subclass calls `super().__init__()`), a class attribute and a method, read through `self` in a method called by the claiming function. Not refused by PYCSL-R445-ATTRIBUTE-NOT-DEFINED.
"""
# pycsl-expected: PASS


class Base:
    K = 2

    def __init__(self) -> None:
        self.a = 1


class Sub(Base):
    def __init__(self) -> None:
        super().__init__()
        self.b = 3

    def g(self) -> int:
        return self.a + self.b + self.K


#@ no_exception \all
def f(p: Sub) -> int:
    return p.g()


if __name__ == "__main__":
    print("result", f(Sub()))
