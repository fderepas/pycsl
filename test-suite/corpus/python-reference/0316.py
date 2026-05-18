"""Test 0316 — Python Reference 3.2.12: I/O objects (also known as file objects) (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_12_b(x: int) -> int:
    """Variation B for I/O objects (also known as file objects)."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_12_b(3) == 6
