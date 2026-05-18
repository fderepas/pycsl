"""Test 0032 — PyCSL Annotation Reference 3.4.3"""
_ = 0  # anchor
#@ ensures \result == a + b
def test_assigns_multiple(a: int, b: int) -> int:
    """Assigns multiple variables: x, y both may be mutated."""
    x = a
    y = b
    return x + y

if __name__ == "__main__":
    assert test_assigns_multiple(3, 7) == 10
