"""Test 0153 — Python Reference 6.5: The power operator"""
_ = 0  # anchor
#@ ensures \result == 8
def test_power_operator() -> int:
    """** is the power operator."""
    return 2 ** 3

if __name__ == "__main__":
    assert test_power_operator() == 8
