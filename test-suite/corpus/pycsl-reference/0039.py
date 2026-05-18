"""Test 0039 — PyCSL Annotation Reference 4.5"""
_ = 0  # anchor
#@ ensures \result == 0
def test_no_string_literals() -> int:
    """String literals are NOT supported in contracts."""
    return 0

if __name__ == "__main__":
    assert test_no_string_literals() == 0
