"""Test 0151 — Python Reference 6.3.3: Calls"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 3
def test_slicings() -> int:
    """a[i:j] slices sequence a."""
    a = [1, 2, 3, 4, 5]
    return len(a[1:4])

if __name__ == "__main__":
    assert test_slicings() == 3
