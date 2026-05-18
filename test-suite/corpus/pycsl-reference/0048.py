"""Test 0048 — PyCSL Annotation Reference 9.2"""
_ = 0  # anchor
#@ ensures \result == 1
def test_exit_code_one() -> int:
    """Exit code 1: verification failed, incomplete, or pipeline error."""
    return 1

if __name__ == "__main__":
    assert test_exit_code_one() == 1
