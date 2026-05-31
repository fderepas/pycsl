"""Test codecs.readbuffer_encode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import codecs  # noqa: F401


#@ requires True
#@ ensures True
def use_readbuffer_encode(x: int) -> int:
    return codecs.readbuffer_encode(x)


if __name__ == "__main__":
    pass
