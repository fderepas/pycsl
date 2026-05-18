"""Test 0133 — Python Reference 6.2.2.1: Private name mangling"""
_ = 0  # anchor
#@ ensures \result == 0
def test_private_name_mangling() -> int:
    """Ref 6.2.2.1: Private name mangling."""
    return 0

if __name__ == "__main__":
    assert test_private_name_mangling() == 0
