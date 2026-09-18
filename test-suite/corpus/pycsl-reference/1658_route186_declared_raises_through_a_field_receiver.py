r"""Test 1658 - ROUTE #186 (gen #29): a callee declaring `#@ raises ValueError when v < 0`, called as `self.inner.go(-1)` under the caller's `#@ no_exception ValueError`, PROVED (CPython ValueError): route #100/#105's key `outer__inner_go` names no function, so the call site got no `assert { not P }`. The key now falls back to the method-name match.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Inner:
    def __init__(self) -> None:
        self.k = 0

    #@ raises ValueError when v < 0
    def go(self, v: int) -> int:
        if v < 0:
            raise ValueError()
        return v


class Outer:
    def __init__(self) -> None:
        self.inner = Inner()

    #@ no_exception ValueError
    #@ ensures \result == 0
    def run(self) -> int:
        self.inner.go(-1)
        return 0
