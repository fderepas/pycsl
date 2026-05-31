"""Test imaplib.ParseFlags L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import imaplib  # noqa: F401


#@ requires True
#@ ensures True
def use_ParseFlags(x: int) -> int:
    return imaplib.ParseFlags(x)


if __name__ == "__main__":
    pass
