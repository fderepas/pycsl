"""Test functools.lru_cache L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import functools  # noqa: F401


#@ requires True
#@ ensures True
def use_lru_cache(x: int) -> int:
    return functools.lru_cache(x)


if __name__ == "__main__":
    pass
