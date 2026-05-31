"""Test fileinput.isstdin L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fileinput  # noqa: F401


#@ requires True
#@ ensures True
def use_isstdin(x: int) -> int:
    return fileinput.isstdin(x)


if __name__ == "__main__":
    pass
