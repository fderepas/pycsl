"""Test 0213 — Python Reference 8.11: Annotations"""
_ = 0  # anchor
#@ ensures \result == 0
def test_annotations_chapter() -> int:
    """Type annotations in function signatures and variable declarations."""
    x: int = 42
    def f(a: int, b: str) -> int:
        return a
    assert f(1, "x") == 1
    return 0

if __name__ == "__main__":
    assert test_annotations_chapter() == 0
