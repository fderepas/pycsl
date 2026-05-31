"""Test gettext.install L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gettext  # noqa: F401


#@ requires True
#@ ensures True
def use_install(x: int) -> int:
    return gettext.install(x)


if __name__ == "__main__":
    pass
