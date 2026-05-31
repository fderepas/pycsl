"""Test functools.cached_property L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import functools  # noqa: F401


#@ requires True
#@ ensures True
def use_cached_property(x: int) -> int:
    return functools.cached_property(x)


if __name__ == "__main__":
    pass
