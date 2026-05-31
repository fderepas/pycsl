"""Test gettext.dpgettext L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gettext  # noqa: F401


#@ requires True
#@ ensures True
def use_dpgettext(x: int) -> int:
    return gettext.dpgettext(x)


if __name__ == "__main__":
    pass
