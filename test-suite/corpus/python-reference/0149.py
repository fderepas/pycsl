"""Test 0149 — Python Reference 6.3.2.3: "Starred" subscriptions"""
_ = 0  # anchor
#@ ensures \result == 0
def test_subscription_class_objects() -> int:
    """C[int] triggers __class_getitem__."""
    assert list[int] is not None
    return 0

if __name__ == "__main__":
    assert test_subscription_class_objects() == 0
