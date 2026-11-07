# F4: #334 residuals 6 / 1 and an override-return-type case
class B:
    def m(self) -> int:
        return 1

    def __init__(self) -> None:
        self.r = self.m()

class S(B):
    def m(self) -> float:
        return 0.5

class U:
    def __init__(self, v) -> None:
        self.r = v

#@ ensures \result == True
def g_init_override(b: B) -> bool:
    return b.r % 1 == 0

#@ ensures \result == True
def g_call_override(b: B) -> bool:
    return b.m() % 1 == 0

#@ ensures \result == True
def g_unannot_init(c: U) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    import rt23h
    rt23h.check([
        ("g_init_override", g_init_override, (S(),), True),
        ("g_call_override", g_call_override, (S(),), True),
        ("g_unannot_init", g_unannot_init, (U(0.5),), True),
    ])
