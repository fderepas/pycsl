"""Test msvcrt.get_osfhandle L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import msvcrt  # noqa: F401


#@ requires True
#@ ensures True
def use_get_osfhandle(x: int) -> int:
    return msvcrt.get_osfhandle(x)


if __name__ == "__main__":
    pass
