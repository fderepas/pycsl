"""Test fcntl.flock L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fcntl  # noqa: F401


#@ requires True
#@ ensures True
def use_flock(x: int) -> int:
    return fcntl.flock(x)


if __name__ == "__main__":
    pass
