r"""Test 5323 -- gen #37 route #387 (expected PASS): control: an `if True:` inside a METHOD body (not a class-body compound statement); PROVED.
"""
# pycsl-expected: PASS
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def get(self) -> int:
        x = 0
        if True:
            x = 1
        return x


#@ ensures \result == 1
def f(obj: C) -> int:
    return obj.get()


if __name__ == "__main__":
    assert f(C()) == 1
