"""Test fnmatch.translate L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fnmatch  # noqa: F401


#@ requires True
#@ ensures True
def use_translate(x: int) -> int:
    return fnmatch.translate(x)


if __name__ == "__main__":
    pass
