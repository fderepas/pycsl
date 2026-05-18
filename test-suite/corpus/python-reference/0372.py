"""Test 0372 — Python Reference 4.1: Structure of a program (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_1_b(x: int) -> int:
    """Variation B for Structure of a program."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_1_b(3) == 6
