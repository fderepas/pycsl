"""Test pathlib.owner L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_owner(x: int) -> int:
    return pathlib.owner(x)


if __name__ == "__main__":
    pass
