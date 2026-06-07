"""Formal tests for pure_lib/csys (colorsys) — universally quantified.

Since PyCSL import stubs don't preserve tuple return types, formal tests
for tuple-returning functions exercise the contracts at body level
(co-located with the implementation). This file tests the int-returning
helpers that ARE importable."""
from pure_lib.csys import _rgb_max, _rgb_min, _hsv_saturation, _hls_saturation, _hsv_p


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result >= r and \result >= g and \result >= b
#@ ensures \result >= 0 and \result <= 1000
def test_rgb_max_is_max(r: int, g: int, b: int) -> int:
    """_rgb_max returns the maximum of three RGB components."""
    return _rgb_max(r, g, b)


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result <= r and \result <= g and \result <= b
#@ ensures \result >= 0 and \result <= 1000
def test_rgb_min_is_min(r: int, g: int, b: int) -> int:
    """_rgb_min returns the minimum of three RGB components."""
    return _rgb_min(r, g, b)


#@ requires 0 <= mx and mx <= 1000
#@ requires 0 <= mn and mn <= mx
#@ ensures \result >= 0
#@ ensures mn == mx ==> \result == 0
def test_hsv_saturation_zero_uniform(mx: int, mn: int) -> int:
    """Uniform color (mx==mn) gives zero saturation."""
    return _hsv_saturation(mx, mn)


#@ requires 0 <= mx and mx <= 1000
#@ requires 0 <= mn and mn <= mx
#@ requires mx > 0
#@ ensures \result == ((mx - mn) * 1000) // mx
def test_hsv_saturation_exact(mx: int, mn: int) -> int:
    """HSV saturation exact formula when mx > 0."""
    return _hsv_saturation(mx, mn)


#@ requires 0 <= mx and mx <= 1000
#@ requires 0 <= mn and mn <= 1000
#@ requires mn < mx
#@ ensures \result >= 0 and \result <= 1000
def test_hls_saturation_bounds(mx: int, mn: int) -> int:
    """HLS saturation is always in [0, 1000]."""
    return _hls_saturation(mx, mn)


#@ requires 0 <= v and v <= 1000
#@ requires 0 <= s and s <= 1000
#@ ensures \result == (v * (1000 - s)) // 1000
#@ ensures \result >= 0 and \result <= v
def test_hsv_p_exact(v: int, s: int) -> int:
    """hsv_p exact formula: v*(1-s)."""
    return _hsv_p(v, s)


#@ requires 0 <= v and v <= 1000
#@ ensures \result == v
def test_hsv_p_zero_saturation(v: int) -> int:
    """p = v when s = 0."""
    return _hsv_p(v, 0)


#@ requires 0 <= v and v <= 1000
#@ ensures \result == 0
def test_hsv_p_full_saturation(v: int) -> int:
    """p = 0 when s = 1000."""
    return _hsv_p(v, 1000)
