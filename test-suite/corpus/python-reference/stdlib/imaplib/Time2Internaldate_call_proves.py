"""Test imaplib.Time2Internaldate L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import imaplib  # noqa: F401


#@ requires True
#@ ensures True
def use_Time2Internaldate(x: int) -> int:
    return imaplib.Time2Internaldate(x)


if __name__ == "__main__":
    pass
