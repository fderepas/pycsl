"""Test 0028 — Python Reference 2.5.4.7: Unrecognized escape sequences"""
_ = 0  # anchor
#@ ensures \result == 0
def test_unrecognized_escape_sequences() -> int:
    """Ref 2.5.4.7: Unrecognized escape sequences."""
    return 0

if __name__ == "__main__":
    assert test_unrecognized_escape_sequences() == 0
