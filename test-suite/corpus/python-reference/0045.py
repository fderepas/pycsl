"""Test 0045 — Python Reference 3.2.5.1: Immutable sequences"""
_ = 0  # anchor
#@ ensures \result == 5
def test_strings() -> int:
    """Strings are immutable sequences of Unicode code points."""
    s = "hello"
    return len(s)

if __name__ == "__main__":
    assert test_strings() == 5
