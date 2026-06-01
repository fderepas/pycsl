"""Test linecache.getline L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import linecache  # noqa: F401


#@ requires True
#@ ensures True
def use_getline(x: int) -> int:
    return linecache.getline(x)


if __name__ == "__main__":
    pass
