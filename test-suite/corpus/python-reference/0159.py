"""Test 0159 — Python Reference 6.10.2: Membership test operations"""
_ = 0  # anchor
#@ ensures \result == 1
def test_membership_test() -> int:
    """in and not in test membership."""
    if 2 in [1, 2, 3]:
        return 1
    return 0

if __name__ == "__main__":
    assert test_membership_test() == 1
