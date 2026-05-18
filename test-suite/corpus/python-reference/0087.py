"""Test 0087 — Python Reference 3.3.4: Customizing instance and subclass checks"""
_ = 0  # anchor
#@ ensures \result == 1
def test_customizing_isinstance_checks() -> int:
    """__instancecheck__ and __subclasscheck__."""
    class C:
        pass
    if isinstance(C(), C):
        return 1
    return 0

if __name__ == "__main__":
    assert test_customizing_isinstance_checks() == 1
