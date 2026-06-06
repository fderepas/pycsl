"""Test pathlib.is_char_device L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_is_char_device(x: int) -> int:
    return pathlib.is_char_device(x)


if __name__ == "__main__":
    pass
