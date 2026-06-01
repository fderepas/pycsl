"""Test linecache.lazycache L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import linecache  # noqa: F401


#@ requires True
#@ ensures True
def use_lazycache(x: int) -> int:
    return linecache.lazycache(x)


if __name__ == "__main__":
    pass
