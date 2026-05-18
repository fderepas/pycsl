"""Test 0104 — Python Reference 4.2.2: Resolution of names"""
_ = 0  # anchor
#@ ensures \result == 0
def test_resolution_of_names() -> int:
    """Ref 4.2.2: Resolution of names."""
    return 0

if __name__ == "__main__":
    assert test_resolution_of_names() == 0
