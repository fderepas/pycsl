"""Test 0154 — PyCSL Annotation Reference 9.2 (variation A)"""
_ = 0  # anchor
#@ ensures \result == 2
def test_exit_code_one_a() -> int:
    """Exit code 1: documents error-path semantics."""
    return 2

if __name__ == "__main__":
    assert test_exit_code_one_a() == 2
