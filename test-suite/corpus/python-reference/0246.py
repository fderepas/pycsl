"""Test 0246 — Python Reference 2.3.1: Keywords (variation B)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == n
def test_keywords_b(n: int) -> int:
    """while keyword with loop."""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_keywords_b(5) == 5
