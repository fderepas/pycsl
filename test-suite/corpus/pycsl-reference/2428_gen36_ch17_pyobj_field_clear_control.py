r"""Test 2428 — gen #36 ch17 S-D (expected PASS): CONTROL, opaque-object carrier: a field no record declares (a trusted `__init__` binds it with `setattr`) is
held in `_pyobj_state`; `self.d.clear()` is the havoc store `setattr_c self <h> (any int)`
under the declared `#@ assigns self.d` (the mirror's `_Unparser.visit_Module` shape).
"""
# pycsl-expected: PASS


def mutable_state(cls):
    return cls


@mutable_state
class C:
    #@ \trusted reviewer: pycsl-self-annotate
    #@ assigns self.d
    def __init__(self):
        setattr(self, "d", {1: 5})

    #@ ensures \result == 0
    #@ assigns self.d
    def m(self) -> int:
        self.d.clear()
        return 0


if __name__ == "__main__":
    c = C()
    assert c.d == {1: 5}
    assert c.m() == 0 and c.d == {}
