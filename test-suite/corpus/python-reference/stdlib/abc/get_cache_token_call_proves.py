"""Test abc.get_cache_token L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import abc  # noqa: F401


#@ requires True
#@ ensures True
def use_get_cache_token(x: int) -> int:
    return abc.get_cache_token(x)


if __name__ == "__main__":
    pass
