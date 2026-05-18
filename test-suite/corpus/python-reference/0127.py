"""Test 0127 — Python Reference 5.6: Replacing the standard import system"""
_ = 0  # anchor
#@ ensures \result == 0
def test_replacing_import() -> int:
    """__import__ can be replaced to customize import behavior."""
    assert callable(__builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__)
    return 0

if __name__ == "__main__":
    assert test_replacing_import() == 0
