"""Test enum.show_flag_values L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import enum  # noqa: F401


#@ requires True
#@ ensures True
def use_show_flag_values(x: int) -> int:
    return enum.show_flag_values(x)


if __name__ == "__main__":
    pass
