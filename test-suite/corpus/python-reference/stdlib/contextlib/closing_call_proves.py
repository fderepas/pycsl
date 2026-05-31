"""Test contextlib.closing L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import contextlib  # noqa: F401


#@ requires True
#@ ensures True
def use_closing(x: int) -> int:
    return contextlib.closing(x)


if __name__ == "__main__":
    pass
