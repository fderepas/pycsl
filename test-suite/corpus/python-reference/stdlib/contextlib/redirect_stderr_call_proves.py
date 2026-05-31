"""Test contextlib.redirect_stderr L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import contextlib  # noqa: F401


#@ requires True
#@ ensures True
def use_redirect_stderr(x: int) -> int:
    return contextlib.redirect_stderr(x)


if __name__ == "__main__":
    pass
