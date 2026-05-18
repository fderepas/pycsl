"""Test 0162 — Python Reference 6.12: Assignment expressions"""
_ = 0  # anchor
#@ ensures \result == 0
def test_assignment_expressions() -> int:
    """Walrus operator :=."""
    data = [1, 2, 3, 4, 5]
    if (n := len(data)) > 3:
        return 0
    return n

if __name__ == "__main__":
    assert test_assignment_expressions() == 0
