"""Test argparse.FileType L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ requires True
#@ ensures True
def use_FileType(x: int) -> int:
    return argparse.FileType(x)


if __name__ == "__main__":
    pass
