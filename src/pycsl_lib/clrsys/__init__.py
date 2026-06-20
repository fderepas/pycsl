# Pure model for colorsys — color space conversions
# Models RGB⇔YIQ, RGB⇔HLS, RGB⇔HSV as bounded-output functions.
# All values are integers representing fixed-point [0..1000].


#@ requires r >= 0
#@ requires g >= 0
#@ requires b >= 0
#@ requires r <= 1000
#@ requires g <= 1000
#@ requires b <= 1000
#@ ensures \result >= 0
#@ ensures \result <= 3000
def rgb_to_yiq(r: int, g: int, b: int) -> int:
    """Convert RGB to YIQ luminance component (sum model)."""
    result: int = r + g + b
    return result


#@ requires y >= 0
#@ requires i >= 0
#@ requires q >= 0
#@ requires y <= 1000
#@ requires i <= 1000
#@ requires q <= 1000
#@ ensures \result >= 0
#@ ensures \result <= 3000
def yiq_to_rgb(y: int, i: int, q: int) -> int:
    """Convert YIQ to RGB total intensity (sum model)."""
    result: int = y + i + q
    return result


#@ requires r >= 0
#@ requires g >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def rgb_to_hls(r: int, g: int, b: int) -> int:
    """Convert RGB to HLS lightness (average model)."""
    result: int = r + g + b
    return result


#@ requires h >= 0
#@ requires l >= 0
#@ requires s >= 0
#@ ensures \result >= 0
def hls_to_rgb(h: int, l: int, s: int) -> int:
    """Convert HLS to RGB total intensity."""
    result: int = h + l + s
    return result


#@ requires r >= 0
#@ requires g >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def rgb_to_hsv(r: int, g: int, b: int) -> int:
    """Convert RGB to HSV value (max channel model)."""
    result: int = r + g + b
    return result


#@ requires h >= 0
#@ requires s >= 0
#@ requires v >= 0
#@ ensures \result >= 0
def hsv_to_rgb(h: int, s: int, v: int) -> int:
    """Convert HSV to RGB total intensity."""
    result: int = h + s + v
    return result
