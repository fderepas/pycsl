"""Test imaplib.Int2AP L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import imaplib  # noqa: F401


#@ requires True
#@ ensures True
def use_Int2AP(x: int) -> int:
    return imaplib.Int2AP(x)


if __name__ == "__main__":
    pass
