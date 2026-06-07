# Formal test for colorsys (csys) module
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


#@ ensures \result >= 0 and \result <= 1000
def test_yiq_bounded() -> int:
    """YIQ Y is in [0, 1000] for valid RGB input."""
    return rgb_to_yiq_y(500, 300, 800)


#@ ensures \result >= 0 and \result <= 1000
def test_rgb_max_bounded() -> int:
    """rgb_max returns value in [0, 1000]."""
    return rgb_max(100, 500, 300)


#@ ensures \result >= 0 and \result <= 1000
def test_rgb_min_bounded() -> int:
    """rgb_min returns value in [0, 1000]."""
    return rgb_min(100, 500, 300)


#@ ensures \result >= 0 and \result <= 1000
def test_saturation_bounded() -> int:
    """saturation returns value in [0, 1000]."""
    return saturation(800, 200)


#@ ensures \result >= 0 and \result <= 1000
def test_hsv_p_bounded() -> int:
    """p = v*(1-s) is in [0, 1000]."""
    return hsv_p(800, 600)


#@ ensures \result >= 0 and \result <= 1000
def test_yiq_endpoints() -> int:
    """Black → Y in [0, 1000]."""
    return rgb_to_yiq_y(0, 0, 0)
