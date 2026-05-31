"""Test gettext.find L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gettext  # noqa: F401


#@ requires True
#@ ensures True
def use_find(x: int) -> int:
    return gettext.find(x)


if __name__ == "__main__":
    pass
