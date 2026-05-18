"""Test 0117 — Python Reference 5.3.3: Import hooks"""
_ = 0  # anchor
#@ ensures \result == 0
def test_import_hooks() -> int:
    """Import hooks customize the import process."""
    import sys
    assert hasattr(sys, "meta_path")
    assert hasattr(sys, "path_hooks")
    return 0

if __name__ == "__main__":
    assert test_import_hooks() == 0
