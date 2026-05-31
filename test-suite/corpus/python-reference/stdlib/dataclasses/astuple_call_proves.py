"""Test dataclasses.astuple L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import dataclasses  # noqa: F401


#@ requires True
#@ ensures True
def use_astuple(x: int) -> int:
    return dataclasses.astuple(x)


if __name__ == "__main__":
    pass
