"""Test 0212 — Python Reference 8.10.3: Generic type aliases"""
_ = 0  # anchor
#@ ensures \result == 0
def test_generic_type_aliases() -> int:
    """Generic type aliases."""
    type Pair[T] = tuple[T, T]
    assert Pair is not None
    return 0

if __name__ == "__main__":
    assert test_generic_type_aliases() == 0
