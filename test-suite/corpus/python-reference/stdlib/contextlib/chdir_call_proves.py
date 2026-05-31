"""Test contextlib.chdir L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import contextlib  # noqa: F401


#@ requires True
#@ ensures True
def use_chdir(x: int) -> int:
    return contextlib.chdir(x)


if __name__ == "__main__":
    pass
