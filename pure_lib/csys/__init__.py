# pure_lib/csys — pure-Python colorsys model
# Named 'csys' to avoid stdlib name clash.
#
# Contracts derived from library_reference/colorsys.rst.
# RST: "Coordinates in all of these color spaces are floating-point values.
#  In the YIQ space, the Y coordinate is between 0 and 1."
# All coordinates in RGB, HLS, HSV are between 0 and 1.
# Modelled as integers scaled 0..1000 representing [0.0, 1.0].


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result >= 0 and \result <= 1000
#@ ensures \result == (300 * r + 590 * g + 110 * b) // 1000
def rgb_to_yiq_y(r: int, g: int, b: int) -> int:
    """Y component of YIQ (luminance). Y = 0.30*R + 0.59*G + 0.11*B.
    RST: 'Y coordinate is between 0 and 1.' → result in [0, 1000]."""
    return (300 * r + 590 * g + 110 * b) // 1000


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result >= 0 and \result <= 1000
def rgb_max(r: int, g: int, b: int) -> int:
    """Return max of three RGB components."""
    mx = r
    if g > mx:
        mx = g
    if b > mx:
        mx = b
    return mx


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result >= 0 and \result <= 1000
def rgb_min(r: int, g: int, b: int) -> int:
    """Return min of three RGB components."""
    mn = r
    if g < mn:
        mn = g
    if b < mn:
        mn = b
    return mn


#@ requires 0 <= mx and mx <= 1000
#@ requires 0 <= mn and mn <= mx
#@ ensures \result >= 0 and \result <= 1000
#@ ensures mn == mx ==> \result == 0
#@ ensures mx > 0 and mn == 0 ==> \result == 1000
#@ ensures mx == 0 ==> \result == 0
#@ ensures mx > 0 ==> \result == ((mx - mn) * 1000) // mx
def saturation(mx: int, mn: int) -> int:
    """HSV saturation: (max-min)/max, or 0 if max==0.
    RST: 'coordinates are all between 0 and 1' → result in [0, 1000].
    Uniform color (max==min) → 0. Pure color (min==0) → 1000."""
    if mx == 0:
        return 0
    diff = mx - mn
    #@ assert 0 <= diff and diff <= mx
    #@ assert diff * 1000 <= mx * 1000
    return (diff * 1000) // mx


#@ requires 0 <= v and v <= 1000
#@ requires 0 <= s and s <= 1000
#@ ensures \result >= 0 and \result <= 1000
#@ ensures \result == (v * (1000 - s)) // 1000
def hsv_p(v: int, s: int) -> int:
    """HSV helper: p = v * (1 - s)."""
    return (v * (1000 - s)) // 1000


#@ requires 0 <= h and h <= 1000
#@ requires 0 <= l and l <= 1000
#@ requires 0 <= s and s <= 1000
#@ ensures \result >= 0
#@ ensures s == 0 ==> \result == l
def hls_to_rgb_helper(h: int, l: int, s: int) -> int:
    """Intermediate HLS→RGB: returns m1 = 2*l - m2.
    RST: 'Convert from HLS to RGB.' When saturation is 0, all channels
    equal lightness (greyscale)."""
    if s == 0:
        return l
    if l <= 500:
        m2 = (l * (1000 + s)) // 1000
    else:
        m2 = l + s - (l * s) // 1000
    m1 = 2 * l - m2
    return m1


#@ requires 0 <= l and l <= 1000
#@ requires 0 <= s and s <= 1000
#@ ensures \result >= 0
def hls_m2(l: int, s: int) -> int:
    """HLS helper: m2 value."""
    if l <= 500:
        return (l * (1000 + s)) // 1000
    return l + s - (l * s) // 1000
