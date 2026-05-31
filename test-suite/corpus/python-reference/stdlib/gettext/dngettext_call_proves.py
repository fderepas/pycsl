"""Test gettext.dngettext L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gettext  # noqa: F401


#@ requires True
#@ ensures True
def use_dngettext(x: int) -> int:
    return gettext.dngettext(x)


if __name__ == "__main__":
    pass
