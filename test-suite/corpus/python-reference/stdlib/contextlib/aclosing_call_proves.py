"""Test contextlib.aclosing L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import contextlib  # noqa: F401


#@ requires True
#@ ensures True
def use_aclosing(x: int) -> int:
    return contextlib.aclosing(x)


if __name__ == "__main__":
    pass
