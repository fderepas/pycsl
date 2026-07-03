# pycsl_lib/csys — pure-Python colorsys
# Named 'csys' to avoid stdlib name clash.
#
# Contracts derived from library_reference/colorsys.rst.
# RST: "Coordinates in all of these color spaces are floating-point values."
# All coordinates modelled as integers scaled 0..1000 representing [0.0, 1.0].
# Each function matches the RST API signature and returns a tuple.
#
# Body-proven: rgb_to_yiq, yiq_to_rgb, _rgb_max, _rgb_min, _hsv_saturation,
#              _hls_saturation, _hsv_p, _hue_offset, rgb_to_hsv
# rgb_to_hsv de-trusted (non-lin-int-div-fixed.md S5): the nonlinear integer-
# division bounds SMT times out on are discharged in the leaf helpers via the
# `sat_bound` / `hue_bound` axioms, cross-validated by __init__.proofs/rocq/
# Colorsys.v + __init__.proofs/lean/Colorsys.lean (Curry-Howard: SMT-timeout is
# a Rocq/Lean proof obligation, never a terminal trust state).
# Trusted bodies (SMT timeout on deep branch + division — de-trust via the same
# leaf-helper + cited-axiom pattern is future work):
#              rgb_to_hls, hls_to_rgb, hsv_to_rgb


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result[0] == (300 * r + 590 * g + 110 * b) // 1000
#@ ensures \result[1] == (599 * r - 277 * g - 322 * b) // 1000
#@ ensures \result[2] == (213 * r - 525 * g + 312 * b) // 1000
#@ ensures \result[0] >= 0 and \result[0] <= 1000
#@ assigns \nothing
def rgb_to_yiq(r: int, g: int, b: int) -> tuple:
    """RST: 'Convert the color from RGB coordinates to YIQ coordinates.'"""
    y = (300 * r + 590 * g + 110 * b) // 1000
    i = (599 * r - 277 * g - 322 * b) // 1000
    q = (213 * r - 525 * g + 312 * b) // 1000
    return (y, i, q)


#@ requires 0 <= y and y <= 1000
#@ ensures \result[0] >= 0 and \result[0] <= 1000
#@ ensures \result[1] >= 0 and \result[1] <= 1000
#@ ensures \result[2] >= 0 and \result[2] <= 1000
#@ assigns \nothing
def yiq_to_rgb(y: int, i: int, q: int) -> tuple:
    """RST: 'Convert the color from YIQ coordinates to RGB coordinates.'"""
    r = y + (948 * i + 624 * q) // 1000
    g = y + (-276 * i - 640 * q) // 1000
    b = y + (-1105 * i + 1729 * q) // 1000
    if r < 0:
        r = 0
    if r > 1000:
        r = 1000
    if g < 0:
        g = 0
    if g > 1000:
        g = 1000
    if b < 0:
        b = 0
    if b > 1000:
        b = 1000
    return (r, g, b)


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result >= 0 and \result <= 1000
#@ ensures \result >= r and \result >= g and \result >= b
#@ ensures (r == g and g == b) ==> \result == r
def _rgb_max(r: int, g: int, b: int) -> int:
    """Max of three RGB components."""
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
#@ ensures \result <= r and \result <= g and \result <= b
#@ ensures (r == g and g == b) ==> \result == r
def _rgb_min(r: int, g: int, b: int) -> int:
    """Min of three RGB components."""
    mn = r
    if g < mn:
        mn = g
    if b < mn:
        mn = b
    return mn


#@ proof rocq Pycsl.Csys.Colorsys.sat_bound
#@ proof lean Pycsl.Csys.Colorsys.sat_bound
#@ requires 0 <= mx and mx <= 1000
#@ requires 0 <= mn and mn <= mx
#@ ensures \result >= 0
#@ ensures \result <= 1000
#@ ensures mn == mx ==> \result == 0
#@ ensures mx > 0 ==> \result == ((mx - mn) * 1000) // mx
#@ ensures mx == 0 ==> \result == 0
def _hsv_saturation(mx: int, mn: int) -> int:
    """HSV saturation: (max-min)/max, or 0 if max==0."""
    if mx == 0:
        return 0
    diff = mx - mn
    #@ assert 0 <= diff and diff <= mx
    return (diff * 1000) // mx


#@ requires 0 <= mx and mx <= 1000
#@ requires 0 <= mn and mn <= 1000
#@ requires mn < mx
#@ ensures \result >= 0 and \result <= 1000
def _hls_saturation(mx: int, mn: int) -> int:
    """HLS saturation: diff/(sum or 2-sum) depending on lightness."""
    diff = mx - mn
    l = (mx + mn) // 2
    #@ assert diff > 0
    if l <= 500:
        #@ assert mx + mn > 0
        s = (diff * 1000) // (mx + mn)
    else:
        #@ assert 2000 - mx - mn > 0
        s = (diff * 1000) // (2000 - mx - mn)
    if s > 1000:
        s = 1000
    return s


#@ requires 0 <= v and v <= 1000
#@ requires 0 <= s and s <= 1000
#@ ensures \result >= 0 and \result <= v
#@ ensures \result == (v * (1000 - s)) // 1000
def _hsv_p(v: int, s: int) -> int:
    """HSV helper: p = v * (1 - s)."""
    return (v * (1000 - s)) // 1000


# --- Public API: HLS/HSV conversions (trusted bodies, sector branching) ---

#@ \trusted reviewer: SMT-timeout-deep-branch
#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result[0] >= 0 and \result[0] <= 1000
#@ ensures \result[1] >= 0 and \result[1] <= 1000
#@ ensures \result[2] >= 0 and \result[2] <= 1000
#@ ensures r == g and g == b ==> \result[1] == 0 and \result[2] == 0
#@ assigns \nothing
def rgb_to_hls(r: int, g: int, b: int) -> tuple:
    """RST: 'Convert the color from RGB coordinates to HLS coordinates.'
    Returns (h, l, s) all in [0, 1000]."""
    mx = _rgb_max(r, g, b)
    mn = _rgb_min(r, g, b)
    l = (mx + mn) // 2
    if mn == mx:
        return (0, l, 0)
    s = _hls_saturation(mx, mn)
    diff = mx - mn
    if r == mx:
        h = ((g - b) * 1000) // (6 * diff)
    elif g == mx:
        h = 333 + ((b - r) * 1000) // (6 * diff)
    else:
        h = 667 + ((r - g) * 1000) // (6 * diff)
    if h < 0:
        h = h + 1000
    return (h, l, s)


#@ \trusted reviewer: SMT-timeout-deep-branch
#@ requires 0 <= h and h <= 1000
#@ requires 0 <= l and l <= 1000
#@ requires 0 <= s and s <= 1000
#@ ensures \result[0] >= 0 and \result[0] <= 1000
#@ ensures \result[1] >= 0 and \result[1] <= 1000
#@ ensures \result[2] >= 0 and \result[2] <= 1000
#@ ensures s == 0 ==> \result[0] == l and \result[1] == l and \result[2] == l
#@ assigns \nothing
def hls_to_rgb(h: int, l: int, s: int) -> tuple:
    """RST: 'Convert the color from HLS coordinates to RGB coordinates.'"""
    if s == 0:
        return (l, l, l)
    if l <= 500:
        m2 = (l * (1000 + s)) // 1000
    else:
        m2 = l + s - (l * s) // 1000
    m1 = 2 * l - m2
    hr = h + 333
    if hr > 1000:
        hr = hr - 1000
    hg = h
    hb = h - 333
    if hb < 0:
        hb = hb + 1000
    if hr < 167:
        rv = m1 + (m2 - m1) * 6 * hr // 1000
    elif hr < 500:
        rv = m2
    elif hr < 667:
        rv = m1 + (m2 - m1) * 6 * (667 - hr) // 1000
    else:
        rv = m1
    if hg < 167:
        gv = m1 + (m2 - m1) * 6 * hg // 1000
    elif hg < 500:
        gv = m2
    elif hg < 667:
        gv = m1 + (m2 - m1) * 6 * (667 - hg) // 1000
    else:
        gv = m1
    if hb < 167:
        bv = m1 + (m2 - m1) * 6 * hb // 1000
    elif hb < 500:
        bv = m2
    elif hb < 667:
        bv = m1 + (m2 - m1) * 6 * (667 - hb) // 1000
    else:
        bv = m1
    if rv < 0:
        rv = 0
    if rv > 1000:
        rv = 1000
    if gv < 0:
        gv = 0
    if gv > 1000:
        gv = 1000
    if bv < 0:
        bv = 0
    if bv > 1000:
        bv = 1000
    return (rv, gv, bv)


#@ proof rocq Pycsl.Csys.Colorsys.hue_bound
#@ proof lean Pycsl.Csys.Colorsys.hue_bound
#@ requires diff > 0
#@ requires (0 - diff) <= num and num <= diff
#@ ensures (0 - 167) <= \result and \result <= 167
def _hue_offset(num: int, diff: int) -> int:
    """Hue sector offset ((num*1000)//(6*diff)), bounded to [-167, 167] by the
    `hue_bound` nonlinear-division axiom (cross-validated in Rocq + Lean)."""
    return (num * 1000) // (6 * diff)


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result[0] >= 0 and \result[0] <= 1000
#@ ensures \result[1] >= 0 and \result[1] <= 1000
#@ ensures \result[2] >= 0 and \result[2] <= 1000
#@ ensures r == g and g == b ==> \result[1] == 0
#@ assigns \nothing
def rgb_to_hsv(r: int, g: int, b: int) -> tuple:
    """RST: 'Convert the color from RGB coordinates to HSV coordinates.'
    The nonlinear-division bounds are discharged in the leaf helpers
    (`_hsv_saturation`, `_hue_offset`) so this body's VC is purely linear."""
    mx = _rgb_max(r, g, b)
    mn = _rgb_min(r, g, b)
    v = mx
    s = _hsv_saturation(mx, mn)
    if mx == mn:
        return (0, s, v)
    diff = mx - mn
    if r == mx:
        h = _hue_offset(g - b, diff)
    elif g == mx:
        h = 333 + _hue_offset(b - r, diff)
    else:
        h = 667 + _hue_offset(r - g, diff)
    #@ assert (0 - 167) <= h and h <= 834
    if h < 0:
        h = h + 1000
    #@ assert 0 <= h and h <= 1000
    return (h, s, v)


#@ \trusted reviewer: SMT-timeout-deep-branch
#@ requires 0 <= h and h <= 1000
#@ requires 0 <= s and s <= 1000
#@ requires 0 <= v and v <= 1000
#@ ensures \result[0] >= 0 and \result[0] <= 1000
#@ ensures \result[1] >= 0 and \result[1] <= 1000
#@ ensures \result[2] >= 0 and \result[2] <= 1000
#@ ensures s == 0 ==> \result[0] == v and \result[1] == v and \result[2] == v
#@ assigns \nothing
def hsv_to_rgb(h: int, s: int, v: int) -> tuple:
    """RST: 'Convert the color from HSV coordinates to RGB coordinates.'"""
    if s == 0:
        return (v, v, v)
    sector = (h * 6) // 1000
    f = (h * 6) - sector * 1000
    p = _hsv_p(v, s)
    q = (v * (1000 - (s * f) // 1000)) // 1000
    t = (v * (1000 - (s * (1000 - f)) // 1000)) // 1000
    if sector == 0:
        rv = v
        gv = t
        bv = p
    elif sector == 1:
        rv = q
        gv = v
        bv = p
    elif sector == 2:
        rv = p
        gv = v
        bv = t
    elif sector == 3:
        rv = p
        gv = q
        bv = v
    elif sector == 4:
        rv = t
        gv = p
        bv = v
    else:
        rv = v
        gv = p
        bv = q
    if rv < 0:
        rv = 0
    if rv > 1000:
        rv = 1000
    if gv < 0:
        gv = 0
    if gv > 1000:
        gv = 1000
    if bv < 0:
        bv = 0
    if bv > 1000:
        bv = 1000
    return (rv, gv, bv)
