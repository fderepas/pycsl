"""Test datetime.dst L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_dst(x: int) -> int:
    return datetime.dst(x)


if __name__ == "__main__":
    pass
