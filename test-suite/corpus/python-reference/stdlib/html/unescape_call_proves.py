"""Test html.unescape L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import html  # noqa: F401


#@ requires True
#@ ensures True
def use_unescape(x: int) -> int:
    return html.unescape(x)


if __name__ == "__main__":
    pass
