"""Test 0112 — Python Reference 5.1: :mod:`importlib`"""
_ = 0  # anchor
#@ ensures \result == 0
def test_importlib() -> int:
    """importlib provides the import implementation."""
    import importlib
    m = importlib.import_module("os")
    assert hasattr(m, "path")
    return 0

if __name__ == "__main__":
    assert test_importlib() == 0
