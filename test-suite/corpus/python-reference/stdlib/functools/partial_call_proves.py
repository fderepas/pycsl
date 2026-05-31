"""Test functools.partial L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import functools  # noqa: F401


#@ requires True
#@ ensures True
def use_partial(x: int) -> int:
    return functools.partial(x)


if __name__ == "__main__":
    pass
