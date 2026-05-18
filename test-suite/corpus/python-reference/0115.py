"""Test 0115 — Python Reference 5.3.1: The module cache"""
_ = 0  # anchor
#@ ensures \result == 0
def test_module_cache() -> int:
    """sys.modules caches imported modules."""
    import sys
    assert "sys" in sys.modules
    return 0

if __name__ == "__main__":
    assert test_module_cache() == 0
