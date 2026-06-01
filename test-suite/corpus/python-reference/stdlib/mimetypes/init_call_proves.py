"""Test mimetypes.init L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mimetypes  # noqa: F401


#@ requires True
#@ ensures True
def use_init(x: int) -> int:
    return mimetypes.init(x)


if __name__ == "__main__":
    pass
