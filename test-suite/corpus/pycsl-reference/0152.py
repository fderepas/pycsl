"""Test 0152 — PyCSL Annotation Reference 9.1 (variation A)"""
_ = 0  # anchor
#@ ensures \result == x
def test_identity(x: int) -> int:
    """Exit code 0: trivially provable identity."""
    return x

if __name__ == "__main__":
    assert test_identity(7) == 7
