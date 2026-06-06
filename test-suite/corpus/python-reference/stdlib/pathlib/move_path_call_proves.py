"""Test pathlib.move_path L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_move_path(x: int) -> int:
    return pathlib.move_path(x)


if __name__ == "__main__":
    pass
