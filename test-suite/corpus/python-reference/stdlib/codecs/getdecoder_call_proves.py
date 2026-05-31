"""Test codecs.getdecoder L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import codecs  # noqa: F401


#@ requires True
#@ ensures True
def use_getdecoder(x: int) -> int:
    return codecs.getdecoder(x)


if __name__ == "__main__":
    pass
