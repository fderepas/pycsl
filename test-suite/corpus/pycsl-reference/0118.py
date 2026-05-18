"""Test 0118 — PyCSL Annotation Reference 3.4.1 (variation A)"""
_ = 0  # anchor
#@ ensures \result == a * b + c
#@ assigns \nothing
def test_assigns_nothing_expr(a: int, b: int, c: int) -> int:
    """Assigns nothing: three-arg pure expression."""
    return a * b + c

if __name__ == "__main__":
    assert test_assigns_nothing_expr(2, 3, 4) == 10
