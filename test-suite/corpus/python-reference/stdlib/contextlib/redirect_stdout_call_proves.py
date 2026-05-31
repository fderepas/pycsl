"""Test contextlib.redirect_stdout L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import contextlib  # noqa: F401


#@ requires True
#@ ensures True
def use_redirect_stdout(x: int) -> int:
    return contextlib.redirect_stdout(x)


if __name__ == "__main__":
    pass
