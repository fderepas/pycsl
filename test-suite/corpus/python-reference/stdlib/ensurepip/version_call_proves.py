"""Test ensurepip.version L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ensurepip  # noqa: F401


#@ requires True
#@ ensures True
def use_version(x: int) -> int:
    return ensurepip.version(x)


if __name__ == "__main__":
    pass
