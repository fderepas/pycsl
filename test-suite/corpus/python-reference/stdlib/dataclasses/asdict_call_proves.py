"""Test dataclasses.asdict L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import dataclasses  # noqa: F401


#@ requires True
#@ ensures True
def use_asdict(x: int) -> int:
    return dataclasses.asdict(x)


if __name__ == "__main__":
    pass
