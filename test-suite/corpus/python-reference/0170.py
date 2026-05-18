"""Test 0170 — Python Reference 7.2.2: Annotated assignment statements"""
_ = 0  # anchor
#@ ensures \result == 0
def test_annotated_assignment() -> int:
    """x: int = 0 with type annotation."""
    x: int = 0
    return x

if __name__ == "__main__":
    assert test_annotated_assignment() == 0
