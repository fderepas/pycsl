"""Test mimetypes.guess_extension L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mimetypes  # noqa: F401


#@ requires True
#@ ensures True
def use_guess_extension(x: int) -> int:
    return mimetypes.guess_extension(x)


if __name__ == "__main__":
    pass
