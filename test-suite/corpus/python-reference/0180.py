"""Test 0180 — Python Reference 7.11.2: Future statements"""
_ = 0  # anchor
#@ ensures \result == 0
def test_future_statements() -> int:
    """Ref 7.11.2: Future statements."""
    return 0

if __name__ == "__main__":
    assert test_future_statements() == 0
