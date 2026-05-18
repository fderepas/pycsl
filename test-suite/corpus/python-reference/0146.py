"""Test 0146 — Python Reference 6.3.1: Attribute references"""
_ = 0  # anchor
#@ ensures \result == 10
def test_attribute_references() -> int:
    """obj.name accesses attribute name on obj."""
    class C:
        x = 10
    return C.x

if __name__ == "__main__":
    assert test_attribute_references() == 10
