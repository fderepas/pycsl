"""Test imaplib.Internaldate2tuple L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import imaplib  # noqa: F401


#@ requires True
#@ ensures True
def use_Internaldate2tuple(x: int) -> int:
    return imaplib.Internaldate2tuple(x)


if __name__ == "__main__":
    pass
