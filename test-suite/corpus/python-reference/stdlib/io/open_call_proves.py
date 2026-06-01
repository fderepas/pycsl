"""Test io.open L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import io  # noqa: F401


#@ requires True
#@ ensures True
def use_open(x: int) -> int:
    return io.open(x)


if __name__ == "__main__":
    pass
