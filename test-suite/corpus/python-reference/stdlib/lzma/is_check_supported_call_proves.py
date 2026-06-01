"""Test lzma.is_check_supported L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import lzma  # noqa: F401


#@ requires True
#@ ensures True
def use_is_check_supported(x: int) -> int:
    return lzma.is_check_supported(x)


if __name__ == "__main__":
    pass
