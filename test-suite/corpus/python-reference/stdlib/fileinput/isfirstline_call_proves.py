"""Test fileinput.isfirstline L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fileinput  # noqa: F401


#@ requires True
#@ ensures True
def use_isfirstline(x: int) -> int:
    return fileinput.isfirstline(x)


if __name__ == "__main__":
    pass
