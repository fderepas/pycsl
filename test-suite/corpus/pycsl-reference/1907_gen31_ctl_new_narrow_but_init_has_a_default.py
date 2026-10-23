r"""Test 1907 — gen #31 CONTROL for 1905 (expected PASS): narrow `__new__`, but `__init__`'s
argument has a DEFAULT.

`__new__(cls)` accepts nothing after `cls` and `__init__(self, n: int = 3)` requires
nothing, so `Holder()` is a construction that works — and it is the construction this file
makes. CPython runs it and `grab()` answers 3.

1905's rule is deliberately the one that admits NO call at all — `__init__`'s MINIMUM
required count above `__new__`'s MAXIMUM acceptable one — rather than the comfortable
version, "`__new__` is narrower than `__init__`", which would refuse this good program.
The (y4) discipline: the comfortable version of a bound is the one to check.

IF THIS FILE EVER FAILS, the rule has widened from "no call can succeed" to "some call
cannot succeed", and it is now refusing programs that run.
"""
# pycsl-expected: PASS
_ = 0  # anchor


class Holder:
    def __new__(cls):
        return super().__new__(cls)

    def __init__(self, n: int = 3):
        self.x = n


#@ ensures \result == 3
def grab() -> int:
    h = Holder()
    return h.x
