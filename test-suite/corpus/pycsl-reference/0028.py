"""Test 0028 — PyCSL Annotation Reference 3.2.8"""
_ = 0  # anchor
#@ requires b != 0
#@ ensures \result == a * b
def test_multiplicative_operators(a: int, b: int) -> int:
    """Multiplicative operators * and / in contracts. / maps to WhyML div."""
    return a * b

if __name__ == "__main__":
    assert test_multiplicative_operators(3, 4) == 12
