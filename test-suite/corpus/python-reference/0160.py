"""Test 0160 — Python Reference 6.10.3: Identity comparisons"""
_ = 0  # anchor
#@ ensures \result == 1
def test_identity_comparisons() -> int:
    """is and is not test identity."""
    a = None
    if a is None:
        return 1
    return 0

if __name__ == "__main__":
    assert test_identity_comparisons() == 1
