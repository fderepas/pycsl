"""Test 0104 — PyCSL Annotation Reference 3.2.3 (variation A)"""
_ = 0  # anchor
#@ ensures \result == 0 or \result == 1
def test_or_binary(x: int) -> int:
    """Or: result is 0 or 1."""
    if x > 0:
        return 1
    return 0

if __name__ == "__main__":
    assert test_or_binary(5) == 1
    assert test_or_binary(-1) == 0
