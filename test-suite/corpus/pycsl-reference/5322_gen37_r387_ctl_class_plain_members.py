r"""Test 5322 -- gen #37 route #387 (expected PASS): control: plain class-body members (an annotated constant, a method); PROVED.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.n: int = 0

    K: int = 5

    #@ ensures \result == 1
    #@ assigns \nothing
    def get(self) -> int:
        return 1


#@ ensures \result == 1
def f(obj: C) -> int:
    return obj.get()


if __name__ == "__main__":
    assert f(C()) == 1
