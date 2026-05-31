"""Test fileinput.fileno L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fileinput  # noqa: F401


#@ requires True
#@ ensures True
def use_fileno(x: int) -> int:
    return fileinput.fileno(x)


if __name__ == "__main__":
    pass
