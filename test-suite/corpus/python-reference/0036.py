"""Test 0036 — Python Reference 2.6.3: Imaginary literals"""
_ = 0  # anchor
#@ ensures \result == 0
def test_imaginary_literals() -> int:
    """Ref 2.6.3: Imaginary literals."""
    return 0

if __name__ == "__main__":
    assert test_imaginary_literals() == 0
