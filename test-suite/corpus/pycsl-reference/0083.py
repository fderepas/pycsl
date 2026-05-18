"""Test 0083 — PyCSL Annotation Reference 3.1.2 (variation B)"""
_ = 0  # anchor
#@ ensures \result == n * n
def test_var_squared(n: int) -> int:
    """Var atom: same variable used twice in contract."""
    return n * n

if __name__ == "__main__":
    assert test_var_squared(6) == 36
