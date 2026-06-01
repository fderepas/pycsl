"""Test locale.gettext L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import locale  # noqa: F401


#@ requires True
#@ ensures True
def use_gettext(x: int) -> int:
    return locale.gettext(x)


if __name__ == "__main__":
    pass
