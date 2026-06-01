"""Test libcst.MetadataWrapper L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import libcst  # noqa: F401


#@ requires True
#@ ensures True
def use_MetadataWrapper(x: int) -> int:
    return libcst.MetadataWrapper(x)


if __name__ == "__main__":
    pass
