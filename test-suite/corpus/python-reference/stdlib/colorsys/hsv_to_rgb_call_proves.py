"""Test colorsys.hsv_to_rgb L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import colorsys  # noqa: F401


#@ requires True
#@ ensures True
def use_hsv_to_rgb(x: int) -> int:
    return colorsys.hsv_to_rgb(x)


if __name__ == "__main__":
    pass
