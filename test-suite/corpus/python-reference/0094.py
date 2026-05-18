"""Test 0094 — Python Reference 3.3.10: Customizing positional arguments in class pattern matching"""
_ = 0  # anchor
#@ ensures \result == 0
def test_type_annotation_objects() -> int:
    """Type annotations and annotated assignment."""
    x: int = 42
    assert x == 42
    return 0

if __name__ == "__main__":
    assert test_type_annotation_objects() == 0
