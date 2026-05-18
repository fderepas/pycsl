"""Test 0098 — PyCSL Annotation Reference 3.1.13 (variation A)"""
_ = 0  # anchor
#@ ensures \result == x * x + 1
#@ assigns \nothing
def test_nothing_squared_plus(x: int) -> int:
    """Nothing: pure computation x^2 + 1."""
    return x * x + 1

if __name__ == "__main__":
    assert test_nothing_squared_plus(3) == 10
