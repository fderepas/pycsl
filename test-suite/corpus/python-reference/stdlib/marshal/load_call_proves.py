"""Test marshal.load L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import marshal  # noqa: F401


#@ requires True
#@ ensures True
def use_load(x: int) -> int:
    return marshal.load(x)


if __name__ == "__main__":
    pass
