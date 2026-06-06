"""abs() ensures non-negative result."""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def safe_abs(x: int) -> int:
    if x < 0:
        return 0 - x
    return x


if __name__ == "__main__":
    assert safe_abs(-3) == 3
    assert safe_abs(5) == 5
