"""Test colorsys.rgb_to_yiq L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import colorsys  # noqa: F401


#@ requires True
#@ ensures True
def use_rgb_to_yiq(x: int) -> int:
    return colorsys.rgb_to_yiq(x)


if __name__ == "__main__":
    pass
