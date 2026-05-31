"""Test dis.show_code L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import dis  # noqa: F401


#@ requires True
#@ ensures True
def use_show_code(x: int) -> int:
    return dis.show_code(x)


if __name__ == "__main__":
    pass
