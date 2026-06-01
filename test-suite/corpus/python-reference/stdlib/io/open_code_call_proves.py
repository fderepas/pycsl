"""Test io.open_code L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import io  # noqa: F401


#@ requires True
#@ ensures True
def use_open_code(x: int) -> int:
    return io.open_code(x)


if __name__ == "__main__":
    pass
