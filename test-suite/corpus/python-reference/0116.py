"""Test 0116 — Python Reference 5.3.2: Finders and loaders"""
_ = 0  # anchor
#@ ensures \result == 0
def test_finders_and_loaders() -> int:
    """Finders locate modules; loaders load them."""
    import sys
    assert len(sys.meta_path) > 0
    return 0

if __name__ == "__main__":
    assert test_finders_and_loaders() == 0
