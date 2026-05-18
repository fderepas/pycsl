"""Test 0015 — Python Reference 2.3.2: Soft Keywords"""
_ = 0  # anchor
#@ ensures \result == x
def test_soft_keywords(x: int) -> int:
    """Soft keywords (match, case, type, _) are context-dependent."""
    match = x  # 'match' used as variable name (soft keyword)
    return match

if __name__ == "__main__":
    assert test_soft_keywords(42) == 42
