"""Test locale.bind_textdomain_codeset L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import locale  # noqa: F401


#@ requires True
#@ ensures True
def use_bind_textdomain_codeset(x: int) -> int:
    return locale.bind_textdomain_codeset(x)


if __name__ == "__main__":
    pass
