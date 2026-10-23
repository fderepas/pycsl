_ = 0  # anchor
#@ act pos:
#@     given x > 0
#@     ensures \result == 1
#@ act neg:
#@     given x < 0
#@     ensures \result == 1
#@ complete pos, neg
def sign(x: int) -> int:
    if x > 0:
        return 1
    if x < 0:
        return 1
    return 0


#@ ensures \result == 99
def probe() -> int:
    return sign(0)
