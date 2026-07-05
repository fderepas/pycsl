"""WL-02 faithful positive twin — Python `/` is TRUE division (returns float).
The faithful real lowering (`from_int a /. from_int b`) makes `5 / 2 == 2.5`
PROVEN at `float` (real) type.

CPython ground truth:  5 / 2 == 2.5   (a float)
PyCSL real lowering:   from_int 5 /. from_int 2 == 2.5  (real division)
"""
_ = 0
#@ ensures \result == 2.5
def f() -> float:
    return 5 / 2

if __name__ == "__main__":
    assert f() == 2.5  # CPython
