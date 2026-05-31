"""Test fileinput.filelineno L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fileinput  # noqa: F401


#@ requires True
#@ ensures True
def use_filelineno(x: int) -> int:
    return fileinput.filelineno(x)


if __name__ == "__main__":
    pass
