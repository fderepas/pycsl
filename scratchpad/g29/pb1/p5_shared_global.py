_ = 0  # anchor

#@ shared _g
_g: int = 0


def tick() -> int:
    global _g
    _g = _g + 1
    return _g


#@ ensures \result == 0
def probe() -> int:
    tick()
    tick()
    return _g
