"""Test 0177 — Python Reference 7.9: The break statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_break_statement() -> int:
    """break exits the nearest loop."""
    for i in range(100):
        if i == 5:
            break
    assert i == 5
    return 0

if __name__ == "__main__":
    assert test_break_statement() == 0
