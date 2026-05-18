"""Test 0096 — Python Reference 3.3.12: Annotations"""
_ = 0  # anchor
#@ ensures \result == 0
def test_annotations() -> int:
    """Ref 3.3.12: Annotations."""
    return 0

if __name__ == "__main__":
    assert test_annotations() == 0
