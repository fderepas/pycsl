"""Test 0176 — Python Reference 7.8: The raise statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_raise_statement() -> int:
    """raise triggers an exception."""
    try:
        raise ValueError("test")
    except ValueError:
        return 0
    return 1

if __name__ == "__main__":
    assert test_raise_statement() == 0
