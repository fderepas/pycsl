# Formal tests for pure_lib/clrsys — colorsys module
from pure_lib.clrsys import rgb_to_yiq, yiq_to_rgb, rgb_to_hls, hls_to_rgb, rgb_to_hsv, hsv_to_rgb


#@ requires r >= 0 and r <= 1000
#@ requires g >= 0 and g <= 1000
#@ requires b >= 0 and b <= 1000
#@ ensures \result >= 0
#@ ensures \result <= 3000
def test_rgb_yiq_bounded(r: int, g: int, b: int) -> int:
    """YIQ output is bounded."""
    return rgb_to_yiq(r, g, b)


#@ requires h >= 0
#@ requires l >= 0
#@ requires s >= 0
#@ ensures \result >= 0
def test_hls_nonneg(h: int, l: int, s: int) -> int:
    """HLS to RGB is non-negative."""
    return hls_to_rgb(h, l, s)


#@ requires r >= 0
#@ requires g >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def test_hsv_nonneg(r: int, g: int, b: int) -> int:
    """HSV conversion is non-negative."""
    return rgb_to_hsv(r, g, b)
