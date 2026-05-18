"""Test 0119 — PyCSL Annotation Reference 3.4.1 (variation B)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result == x
#@ assigns \nothing
def test_assigns_nothing_identity(x: int) -> int:
    """Assigns nothing: identity function."""
    return x

if __name__ == "__main__":
    assert test_assigns_nothing_identity(42) == 42
