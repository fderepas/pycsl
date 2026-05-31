"""Test dataclasses.dataclass L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import dataclasses  # noqa: F401


#@ requires True
#@ ensures True
def use_dataclass(x: int) -> int:
    return dataclasses.dataclass(x)


if __name__ == "__main__":
    pass
