try:
    _z = 1 // 0
    def g(x: int) -> int:
        return x
except ZeroDivisionError:
    pass
