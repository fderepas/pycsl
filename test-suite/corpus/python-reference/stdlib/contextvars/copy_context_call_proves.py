"""Test contextvars.copy_context L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import contextvars  # noqa: F401


#@ requires True
#@ ensures True
def use_copy_context(x: int) -> int:
    return contextvars.copy_context(x)


if __name__ == "__main__":
    pass
