# Formal test for colorsys (csys) module — universally quantified
#
# Based on library_reference/colorsys.rst:
#   "Coordinates in all of these color spaces are floating-point values."
#   "In the YIQ space, the Y coordinate is between 0 and 1."
#   "In all other spaces, the coordinates are all between 0 and 1."
#
# Tests exercise the strengthened contracts:
#   - rgb_to_yiq_y: result in [0, 1000]
#   - saturation: uniform → 0, pure → 1000
#   - hls_to_rgb_helper: zero saturation → result == l

from pure_lib.csys import rgb_to_yiq_y, rgb_max, rgb_min, saturation, hsv_p, hls_to_rgb_helper


#@ requires r >= 0 and r <= 1000
#@ requires g >= 0 and g <= 1000
#@ requires b >= 0 and b <= 1000
#@ ensures \result >= 0 and \result <= 1000
def test_yiq_bounded(r: int, g: int, b: int) -> int:
    """YIQ Y is in [0, 1000] for all valid RGB inputs."""
    return rgb_to_yiq_y(r, g, b)


#@ requires r >= 0 and r <= 1000
#@ requires g >= 0 and g <= 1000
#@ requires b >= 0 and b <= 1000
#@ ensures \result >= 0 and \result <= 1000
def test_rgb_max_bounded(r: int, g: int, b: int) -> int:
    """rgb_max returns value in [0, 1000] for all valid inputs."""
    return rgb_max(r, g, b)


#@ requires r >= 0 and r <= 1000
#@ requires g >= 0 and g <= 1000
#@ requires b >= 0 and b <= 1000
#@ ensures \result >= 0 and \result <= 1000
def test_rgb_min_bounded(r: int, g: int, b: int) -> int:
    """rgb_min returns value in [0, 1000] for all valid inputs."""
    return rgb_min(r, g, b)


#@ requires mx >= 0 and mx <= 1000
#@ requires mn >= 0 and mn <= mx
#@ ensures \result >= 0 and \result <= 1000
def test_saturation_bounded(mx: int, mn: int) -> int:
    """saturation is in [0, 1000] for all valid mx, mn."""
    return saturation(mx, mn)


#@ requires mx >= 1 and mx <= 1000
#@ ensures \result == 1000
def test_saturation_pure(mx: int) -> int:
    """saturation(mx, 0) == 1000 for all mx > 0. Pure color."""
    return saturation(mx, 0)


#@ requires c >= 0 and c <= 1000
#@ ensures \result == 0
def test_saturation_uniform(c: int) -> int:
    """saturation(c, c) == 0 for all c. Uniform color has no saturation."""
    return saturation(c, c)


#@ requires v >= 0 and v <= 1000
#@ requires s >= 0 and s <= 1000
#@ ensures \result >= 0 and \result <= 1000
def test_hsv_p_bounded(v: int, s: int) -> int:
    """hsv_p(v, s) in [0, 1000] for all valid inputs."""
    return hsv_p(v, s)


#@ requires h >= 0 and h <= 1000
#@ requires l >= 0 and l <= 1000
#@ ensures \result == l
def test_hls_greyscale(h: int, l: int) -> int:
    """hls_to_rgb_helper(h, l, 0) == l for all h, l. Zero saturation → greyscale."""
    return hls_to_rgb_helper(h, l, 0)
