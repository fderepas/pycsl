"""Test gettext.pgettext L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gettext  # noqa: F401


#@ requires True
#@ ensures True
def use_pgettext(x: int) -> int:
    return gettext.pgettext(x)


if __name__ == "__main__":
    pass
