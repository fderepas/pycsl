"""Test 0040 — PyCSL Annotation Reference 4.6"""
_ = 0  # anchor
#@ ensures \result == 1
def test_no_true_false_none() -> int:
    """True/False/None are NOT supported in contracts. Use 1==1 / 1==0."""
    return 1

if __name__ == "__main__":
    assert test_no_true_false_none() == 1
