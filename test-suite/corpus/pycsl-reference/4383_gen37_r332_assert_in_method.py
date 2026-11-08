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
    # CPython ground truth: this call RAISES (see the docstring); no handler, because a
    # handler that can catch AssertionError around an assert is refused (route 16).
    print(C().m())
