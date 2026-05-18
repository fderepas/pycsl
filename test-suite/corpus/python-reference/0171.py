"""Test 0171 — Python Reference 7.3: The assert statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_assert_statement() -> int:
    """assert expr raises AssertionError if false."""
    assert 1 + 1 == 2
    return 0

if __name__ == "__main__":
    assert test_assert_statement() == 0
