"""Test fcntl.lockf L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fcntl  # noqa: F401


#@ requires True
#@ ensures True
def use_lockf(x: int) -> int:
    return fcntl.lockf(x)


if __name__ == "__main__":
    pass
