"""Test pathlib.write_text L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_write_text(x: int) -> int:
    return pathlib.write_text(x)


if __name__ == "__main__":
    pass
