"""Test 0078 — Python Reference 3.3.2.3: Invoking Descriptors"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 42
def test_implementing_descriptors() -> int:
    """Descriptors define __get__, __set__, __delete__."""
    class Desc:
        def __set_name__(self, owner, name):
            self._name = "_" + name
        def __get__(self, obj, tp=None):
            if obj is None:
                return self
            return getattr(obj, self._name, 0)
        def __set__(self, obj, val):
            setattr(obj, self._name, val)
    class C:
        x = Desc()
    c = C()
    c.x = 42
    return c.x

if __name__ == "__main__":
    assert test_implementing_descriptors() == 42
