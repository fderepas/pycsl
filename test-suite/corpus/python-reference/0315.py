"""Test 0315 — Python Reference 3.2.12: I/O objects (also known as file objects) (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_12_a(x: int) -> int:
    """Variation A for I/O objects (also known as file objects)."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_12_a(4) == 5
