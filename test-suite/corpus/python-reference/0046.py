"""Test 0046 — Python Reference 3.2.5.2: Mutable sequences"""
_ = 0  # anchor
#@ ensures \result == 3
def test_tuples() -> int:
    """Tuples are immutable sequences."""
    t = (10, 20, 30)
    return len(t)

if __name__ == "__main__":
    assert test_tuples() == 3
