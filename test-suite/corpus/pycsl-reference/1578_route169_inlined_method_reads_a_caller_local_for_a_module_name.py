r"""Test 1578 - ROUTE #169 (gen #29): a method on a module-global instance reads the module constant `K = 3`; its caller binds a local `K = 9` and calls `_g.f()`. The inliner spliced `return K` into the caller, where `K` is the caller's local, and `\result == 9` PROVED (CPython 3). A spliced identifier the caller binds is now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
K = 3


class C:
    def __init__(self, x: int) -> None:
        self.x = x

    def f(self) -> int:
        return K


_g = C(0)


#@ ensures \result == 9
def probe() -> int:
    K = 9
    return _g.f()
