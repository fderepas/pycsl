"""Test 0371 — Python Reference 4.1: Structure of a program (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_1_a(x: int) -> int:
    """Variation A for Structure of a program."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_1_a(4) == 5
