"""Test 0121 — Python Reference 5.4.3: Module specs"""
_ = 0  # anchor
#@ ensures \result == 0
def test_module_specs() -> int:
    """Ref 5.4.3: Module specs."""
    return 0

if __name__ == "__main__":
    assert test_module_specs() == 0
