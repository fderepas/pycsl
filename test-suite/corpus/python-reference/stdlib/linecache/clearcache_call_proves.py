"""Test linecache.clearcache L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import linecache  # noqa: F401


#@ requires True
#@ ensures True
def use_clearcache(x: int) -> int:
    return linecache.clearcache(x)


if __name__ == "__main__":
    pass
