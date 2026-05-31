"""Test functools.cmp_to_key L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import functools  # noqa: F401


#@ requires True
#@ ensures True
def use_cmp_to_key(x: int) -> int:
    return functools.cmp_to_key(x)


if __name__ == "__main__":
    pass
