"""Test 0048 — Python Reference 3.2.7.1: Dictionaries"""
_ = 0  # anchor
#@ ensures \result == 3
def test_sets() -> int:
    """set is mutable."""
    s = {1, 2, 3}
    s.add(4)
    s.discard(4)
    return len(s)

if __name__ == "__main__":
    assert test_sets() == 3
