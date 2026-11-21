# route #510 residual (corpus 8297): `type C` in a `try` body at module scope rebinds the class `C`
class C:
    def __init__(self, v: int) -> None:
        self.v = v

    #@ ensures \result == self.v
    def get(self) -> int:
        return self.v


try:
    type C = int
except Exception:
    pass
