"""Test gettext.textdomain L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gettext  # noqa: F401


#@ requires True
#@ ensures True
def use_textdomain(x: int) -> int:
    return gettext.textdomain(x)


if __name__ == "__main__":
    pass
