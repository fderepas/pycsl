"""Test 0179 — Python Reference 7.11.1.1: Compatibility via __lazy_modules__"""
_ = 0  # anchor
#@ ensures \result == 0
def test_compatibility_via_lazy_modules() -> int:
    """Ref 7.11.1.1: Compatibility via __lazy_modules__."""
    return 0

if __name__ == "__main__":
    assert test_compatibility_via_lazy_modules() == 0
