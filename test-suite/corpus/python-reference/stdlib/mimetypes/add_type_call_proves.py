"""Test mimetypes.add_type L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mimetypes  # noqa: F401


#@ requires True
#@ ensures True
def use_add_type(x: int) -> int:
    return mimetypes.add_type(x)


if __name__ == "__main__":
    pass
