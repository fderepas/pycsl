"""Test datetime.strftime L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import datetime  # noqa: F401


#@ requires True
#@ ensures True
def use_strftime(x: int) -> int:
    return datetime.strftime(x)


if __name__ == "__main__":
    pass
