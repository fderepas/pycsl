# Formal test for colorsys (csys) module
#
# Based on library_reference/colorsys.rst:
#   "Coordinates in all of these color spaces are floating-point values...
#    between 0 and 1" — we model as [0, 1000].
#
# Tests verify postconditions from csys contracts:
#   - rgb_to_yiq_y: ensures result >= 0
#   - rgb_max: ensures 0 <= result <= 1000
#   - saturation: ensures 0 <= result <= 1000
#   - hsv_p: ensures 0 <= result <= 1000

from pure_lib.csys import rgb_to_yiq_y, rgb_max, rgb_min, saturation, hsv_p


#@ ensures \result >= 0
def test_yiq_nonneg() -> int:
    """YIQ luminance is non-negative for valid input."""
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


#@ ensures \result >= 0
def test_yiq_black() -> int:
    """Black → Y >= 0."""
    return rgb_to_yiq_y(0, 0, 0)
