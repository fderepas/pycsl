"""Test 0155 — PyCSL Annotation Reference 9.2 (variation B)"""
_ = 0  # anchor
#@ ensures \result == x + x
def test_exit_code_one_b(x: int) -> int:
    """Exit code 1: documents error-path semantics (paired sum)."""
    return x + x

if __name__ == "__main__":
    assert test_exit_code_one_b(3) == 6
