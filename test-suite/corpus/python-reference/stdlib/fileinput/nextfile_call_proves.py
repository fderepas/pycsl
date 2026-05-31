"""Test fileinput.nextfile L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fileinput  # noqa: F401


#@ requires True
#@ ensures True
def use_nextfile(x: int) -> int:
    return fileinput.nextfile(x)


if __name__ == "__main__":
    pass
