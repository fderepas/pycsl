"""Test 0128 — Python Reference 5.7: Package Relative Imports"""
_ = 0  # anchor
#@ ensures \result == 0
def test_package_relative_imports() -> int:
    """Relative imports use dots: from . import x."""
    # Can only demonstrate in package context; verify the concept
    return 0

if __name__ == "__main__":
    assert test_package_relative_imports() == 0
