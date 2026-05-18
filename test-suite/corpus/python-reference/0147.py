"""Test 0147 — Python Reference 6.3.2.1: Slicings"""
_ = 0  # anchor
#@ ensures \result == 2
def test_subscriptions() -> int:
    """a[i] accesses element i of sequence a."""
    a = [1, 2, 3]
    return a[1]

if __name__ == "__main__":
    assert test_subscriptions() == 2
