"""Test pathlib.read_text L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_read_text(x: int) -> int:
    return pathlib.read_text(x)


if __name__ == "__main__":
    pass
