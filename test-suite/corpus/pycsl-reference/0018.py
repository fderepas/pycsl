"""Test 0018 — PyCSL Annotation Reference 3.1.11"""
_ = 0  # anchor
#@ requires \length2d(mat, m, n)
#@ requires m >= 1 and n >= 1
#@ ensures \result == mat[0][0]
def test_length2d(mat: list, m: int, n: int) -> int:
    """Length2D atom: \length2d(a, m, n) asserts m rows of length n."""
    return mat[0][0]

if __name__ == "__main__":
    assert test_length2d([[1, 2], [3, 4]], 2, 2) == 1
