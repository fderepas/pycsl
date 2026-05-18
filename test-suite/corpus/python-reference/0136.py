"""Test 0136 — Python Reference 6.2.4: Parenthesized forms"""
_ = 0  # anchor
#@ ensures \result == 6
def test_displays_for_containers() -> int:
    """Displays: list, set, dict displays."""
    a = [1, 2, 3]
    return sum(a)

if __name__ == "__main__":
    assert test_displays_for_containers() == 6
