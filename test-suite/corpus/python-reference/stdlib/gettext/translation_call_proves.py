"""Test gettext.translation L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gettext  # noqa: F401


#@ requires True
#@ ensures True
def use_translation(x: int) -> int:
    return gettext.translation(x)


if __name__ == "__main__":
    pass
