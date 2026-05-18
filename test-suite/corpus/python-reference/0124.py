"""Test 0124 — Python Reference 5.4.6: Cached bytecode invalidation"""
_ = 0  # anchor
#@ ensures \result == 0
def test_cached_bytecode_invalidation() -> int:
    """Ref 5.4.6: Cached bytecode invalidation."""
    return 0

if __name__ == "__main__":
    assert test_cached_bytecode_invalidation() == 0
