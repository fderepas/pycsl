#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result >= 0 and \result <= 1000
#@ ensures \result >= r and \result >= g and \result >= b
#@ ensures \result == r or \result == g or \result == b
def _rgb_max(r: int, g: int, b: int) -> int:
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
#@ ensures \result == r or \result == g or \result == b
def _rgb_min(r: int, g: int, b: int) -> int:
    mn = r
    if g < mn:
        mn = g
    if b < mn:
        mn = b
    return mn


#@ requires 0 <= mx and mx <= 1000
#@ requires 0 <= mn and mn <= mx
#@ ensures \result >= 0
#@ ensures \result <= 1000
#@ ensures mn == mx ==> \result == 0
#@ ensures mx > 0 ==> \result == ((mx - mn) * 1000) // mx
#@ ensures mx == 0 ==> \result == 0
def _hsv_saturation(mx: int, mn: int) -> int:
    if mx == 0:
        return 0
    diff = mx - mn
    #@ assert 0 <= diff and diff <= mx
    return (diff * 1000) // mx


#@ requires diff > 0
#@ requires (0 - diff) <= num and num <= diff
#@ ensures (0 - 167) <= \result and \result <= 167
def _hue_offset(num: int, diff: int) -> int:
    return (num * 1000) // (6 * diff)


#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result[0] >= 0 and \result[0] <= 1000
#@ ensures \result[1] >= 0 and \result[1] <= 1000
#@ ensures \result[2] >= 0 and \result[2] <= 1000
#@ ensures r == g and g == b ==> \result[1] == 0
#@ ensures \result[2] == 0
#@ assigns \nothing
def rgb_to_hsv(r: int, g: int, b: int) -> tuple:
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
    if h < 0:
        h = h + 1000
    return (h, s, v)
