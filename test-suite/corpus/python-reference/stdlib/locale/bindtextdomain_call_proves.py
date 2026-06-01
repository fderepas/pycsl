"""Test locale.bindtextdomain L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import locale  # noqa: F401


#@ requires True
#@ ensures True
def use_bindtextdomain(x: int) -> int:
    return locale.bindtextdomain(x)


if __name__ == "__main__":
    pass
