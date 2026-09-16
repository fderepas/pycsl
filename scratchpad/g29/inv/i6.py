r"""G29 INV6 — route #165 control: an outside store that KEEPS the invariant."""
_ = 0  # anchor


#@ class invariant self.x >= 0
class C:
    def __init__(self) -> None:
        self.x = 1

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.x


#@ ensures \result >= 0
def probe() -> int:
    c = C()
    c.x = 7
    return c.get()
