"""Test libcst.metadata_resolve L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import libcst  # noqa: F401


#@ requires True
#@ ensures True
def use_metadata_resolve(x: int) -> int:
    return libcst.metadata_resolve(x)


if __name__ == "__main__":
    pass
