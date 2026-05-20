"""Test 0076 — Python Reference 3.3.2.1: Customizing module attribute access"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 10
def test_customizing_attribute_access() -> int:
    """__getattr__, __getattribute__, __setattr__, __delattr__."""
    class C:
        def __init__(self):
            self._d = {}
        def __getattr__(self, name):
            return self._d.get(name, 0)
        def __setattr__(self, name, val):
            if name == "_d":
                super().__setattr__(name, val)
            else:
                self._d[name] = val
    c = C()
    c.x = 10
    return c.x

if __name__ == "__main__":
    assert test_customizing_attribute_access() == 10
