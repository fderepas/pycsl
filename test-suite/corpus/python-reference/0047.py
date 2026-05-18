"""Test 0047 — Python Reference 3.2.6: Set types"""
_ = 0  # anchor
#@ ensures \result == 3
def test_sequences_mutable() -> int:
    """Mutable sequences: lists, bytearrays."""
    a = [1, 2, 3]
    return len(a)

if __name__ == "__main__":
    assert test_sequences_mutable() == 3
