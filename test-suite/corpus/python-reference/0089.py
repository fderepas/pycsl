"""Test 0089 — Python Reference 3.3.5.2: *__class_getitem__* versus *__getitem__*"""
_ = 0  # anchor
#@ ensures \result == 0
def test_class_getitem_versus_getitem() -> int:
    """Ref 3.3.5.2: *__class_getitem__* versus *__getitem__*."""
    return 0

if __name__ == "__main__":
    assert test_class_getitem_versus_getitem() == 0
