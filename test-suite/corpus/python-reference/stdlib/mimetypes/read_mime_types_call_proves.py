"""Test mimetypes.read_mime_types L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mimetypes  # noqa: F401


#@ requires True
#@ ensures True
def use_read_mime_types(x: int) -> int:
    return mimetypes.read_mime_types(x)


if __name__ == "__main__":
    pass
