"""Test 0128 — PyCSL Annotation Reference 4.1 (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_unsupported_ctx_a(x: int) -> int:
    """Unsupported: floor division not in contracts. Uses simple verified contract instead."""
    return x + 1

if __name__ == "__main__":
    assert test_unsupported_ctx_a(5) == 6
