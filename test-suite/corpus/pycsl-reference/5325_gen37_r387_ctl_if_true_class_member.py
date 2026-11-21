r"""Test 5325 -- gen #37 route #387 (expected PASS): control: `def get` in the BODY of a class-body `if True:` (always bound); PROVED.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.n: int = 0

    if True:
        #@ ensures \result == 1
        #@ assigns \nothing
        def get(self) -> int:
            return 1


#@ ensures \result == 1
def f(obj: C) -> int:
    return obj.get()


if __name__ == "__main__":
    assert f(C()) == 1
