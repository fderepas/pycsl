"""Test 0106 — Python Reference 4.2.4: Lazy evaluation"""
_ = 0  # anchor
#@ ensures \result == 0
def test_lazy_evaluation() -> int:
    """Ref 4.2.4: Lazy evaluation."""
    return 0

if __name__ == "__main__":
    assert test_lazy_evaluation() == 0
