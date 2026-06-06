"""Test pathlib.group_name L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_group_name(x: int) -> int:
    return pathlib.group_name(x)


if __name__ == "__main__":
    pass
