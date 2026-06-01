"""Test mimetypes.guess_all_extensions L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mimetypes  # noqa: F401


#@ requires True
#@ ensures True
def use_guess_all_extensions(x: int) -> int:
    return mimetypes.guess_all_extensions(x)


if __name__ == "__main__":
    pass
