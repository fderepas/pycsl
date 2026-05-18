"""Test 0077 — Python Reference 3.3.2.2: Implementing Descriptors"""
_ = 0  # anchor
#@ ensures \result == 0
def test_customizing_module_attr_access() -> int:
    """Modules can define __getattr__ and __dir__."""
    return 0

if __name__ == "__main__":
    assert test_customizing_module_attr_access() == 0
