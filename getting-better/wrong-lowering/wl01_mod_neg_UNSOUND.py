"""WL-01b UNSOUND — Python `%` (floored modulo) on a negative divisor -> Euclidean mod.
CPython:  7 % (-2) == -1   (sign follows divisor)
Why3:     mod 7 (-2) == 1   (nonneg remainder)
Detector D3: PyCSL PROVES the FALSE `\result == 1`."""
_ = 0
#@ ensures \result == 1
def f() -> int:
    return 7 % (-2)

if __name__ == "__main__":
    assert f() == -1  # CPython
