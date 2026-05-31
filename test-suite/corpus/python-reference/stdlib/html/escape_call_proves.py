"""Test html.escape L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import html  # noqa: F401


#@ requires True
#@ ensures True
def use_escape(x: int) -> int:
    return html.escape(x)


if __name__ == "__main__":
    pass
