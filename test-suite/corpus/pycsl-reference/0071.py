"""Test 0071 — PyCSL Annotation Reference 2.1.3 (variation B)"""
_ = 0  # anchor
#@ ensures \result == a + b
#@ assigns \nothing
def test_pure_function(a: int, b: int) -> int:
    """Pure function: assigns nothing, only returns a value."""
    return a + b

if __name__ == "__main__":
    assert test_pure_function(10, 20) == 30
