"""Helper for corpus 7269 (route #466): `g` is bound after a raising statement in `try`."""
try:
    X = 1 // 0

    def g(x: int) -> int:
        return x
except ZeroDivisionError:
    pass
