"""Test codecs.unregister L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import codecs  # noqa: F401


#@ requires True
#@ ensures True
def use_unregister(x: int) -> int:
    return codecs.unregister(x)


if __name__ == "__main__":
    pass
