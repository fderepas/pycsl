"""Test locale.nl_langinfo L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import locale  # noqa: F401


#@ requires True
#@ ensures True
def use_nl_langinfo(x: int) -> int:
    return locale.nl_langinfo(x)


if __name__ == "__main__":
    pass
