"""Test 0023 — Python Reference 2.5.4.2: Escaped characters"""
_ = 0  # anchor
#@ ensures \result == 0
def test_escaped_characters() -> int:
    """Ref 2.5.4.2: Escaped characters."""
    return 0

if __name__ == "__main__":
    assert test_escaped_characters() == 0
