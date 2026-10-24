r"""Test 4383 -- gen #37 route #332 (expected FAIL): a failing `assert self.v == 2` in a METHOD under `no_exception \all` PROVED (CPython raises AssertionError). FAILS on the AssertionError obligation.
"""
# pycsl-expected: FAIL
class C:
    def __init__(self) -> None:
        self.v = 1

    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_exception \all
    def m(self) -> int:
        assert self.v == 2
        return 7

if __name__ == "__main__":
    try:
        print(C().m())
    except (AssertionError, IndexError) as e:
        print("CPython raises", type(e).__name__)
