"""Test 0060 — Python Reference 3.2.9.2: Other writable attributes on module objects"""
_ = 0  # anchor
#@ ensures \result == 6
def test_instance_methods() -> int:
    """Instance methods are bound to an object."""
    class C:
        def __init__(self, v):
            self._v = v
        def get(self):
            return self._v
    return C(6).get()

if __name__ == "__main__":
    assert test_instance_methods() == 6
