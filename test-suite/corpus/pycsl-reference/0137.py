"""Test 0137 — PyCSL Annotation Reference 4.5 (variation B)"""
_ = 0  # anchor
#@ ensures \result == a + b
def test_unsupported_ctx_b(a: int, b: int) -> int:
    """Unsupported: string literals not in contracts. Uses simple verified contract instead."""
    return a + b

if __name__ == "__main__":
    assert test_unsupported_ctx_b(3, 4) == 7
