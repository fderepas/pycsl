r"""Test 2429 — gen #36 ch17 S-D (expected FAIL): FRAME twin of 2428: the same opaque-object clear under `#@ assigns \nothing` is an unlisted
write of `_pyobj_state` and must be rejected.
"""
# pycsl-expected: FAIL


def mutable_state(cls):
    return cls


@mutable_state
class C:
    #@ \trusted reviewer: pycsl-self-annotate
    #@ assigns self.d
    def __init__(self):
        setattr(self, "d", {1: 5})

    #@ ensures \result == 0
    #@ assigns \nothing
    def m(self) -> int:
        self.d.clear()
        return 0


if __name__ == "__main__":
    c = C()
    assert c.d == {1: 5}
    assert c.m() == 0 and c.d == {}
