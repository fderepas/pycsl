"""Test 0118 — Python Reference 5.3.4: The meta path"""
_ = 0  # anchor
#@ ensures \result == 0
def test_meta_path() -> int:
    """sys.meta_path contains meta path finders."""
    import sys
    assert isinstance(sys.meta_path, list)
    return 0

if __name__ == "__main__":
    assert test_meta_path() == 0
