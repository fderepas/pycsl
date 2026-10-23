r"""Test 2064 — gen #36 (expected PASS): a plain-class (no `@mutable_state`) method that stores
a RECORD field (`self.n = 1`) beside an attribute the record does not carry (`self.tag = 7`,
the abstract `setattr_*` store). The coarse `writes { _pyobj_state }` the second store adds was
the method's ONLY `writes`, so Why3 rejected the first store ("unlisted write effect"). The
clause now also lists the declared `#@ assigns` field the record carries, and Why3 still checks
the body against it. Twins: 2065 / 2066 (must FAIL).
"""
# pycsl-expected: PASS


class Acc:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == 1
    #@ assigns self.n, self.tag
    def mark(self) -> None:
        self.n = 1
        self.tag = 7
