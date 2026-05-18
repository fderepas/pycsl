"""Test 0042 — PyCSL Annotation Reference 4.8"""
_ = 0  # anchor
#@ ensures \result == n * n
def test_no_list_comprehensions(n: int) -> int:
    """List comprehensions are NOT supported in contracts."""
    return n * n

if __name__ == "__main__":
    assert test_no_list_comprehensions(4) == 16
