"""Test 0025 — PyCSL Annotation Reference 3.2.5"""
_ = 0  # anchor
#@ ensures \result == 1 or \result != 1
def test_equality_operators(x: int) -> int:
    """Equality operators == and != in contracts."""
    return x

if __name__ == "__main__":
    assert test_equality_operators(1) == 1
