"""Test 0005 — Python Reference 2.1.3: Comments"""
# This is a regular comment
#@ ensures \result == x * 2
def test_comments(x: int) -> int:
    """Comments start with # and are ignored (except #@ for PyCSL)."""
    # another comment
    return x * 2  # inline comment

if __name__ == "__main__":
    assert test_comments(5) == 10
