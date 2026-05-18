"""Test 0148 — Python Reference 6.3.2.2: Comma-separated subscripts"""
_ = 0  # anchor
#@ ensures \result == 0
def test_formal_subscription_semantics() -> int:
    """Subscription calls __getitem__."""
    class C:
        def __getitem__(self, k):
            return k * 2
    assert C()[5] == 10
    return 0

if __name__ == "__main__":
    assert test_formal_subscription_semantics() == 0
