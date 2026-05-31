"""Test glob.escape L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import glob  # noqa: F401


#@ requires True
#@ ensures True
def use_escape(x: int) -> int:
    return glob.escape(x)


if __name__ == "__main__":
    pass
