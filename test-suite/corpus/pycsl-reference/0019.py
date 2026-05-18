"""Test 0019 — PyCSL Annotation Reference 3.1.12"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \length2d(mat, 3, 3)
#@ requires \valid2d(mat, i, j)
#@ requires 0 <= i and i < 3 and 0 <= j and j < 3
#@ ensures \result == mat[i][j]
def test_valid2d(mat: list, i: int, j: int) -> int:
    """Valid2D atom: \valid2d(a, i, j) asserts (i,j) is a valid 2D index."""
    return mat[i][j]

if __name__ == "__main__":
    m = [[1,2,3],[4,5,6],[7,8,9]]
    assert test_valid2d(m, 1, 2) == 6
