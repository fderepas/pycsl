# F5: stores into an (unannotated, int-inferred) field made OUTSIDE the class hierarchy (__main__, setattr) are not in the #334 census
class C:
    def __init__(self) -> None:
        self.r = 0

#@ ensures \result == True
def g(c: C) -> bool:
    return c.r % 1 == 0

if __name__ == "__main__":
    import rt23h
    c = C()
    c.r = 0.5
    d = C()
    setattr(d, "r", 0.25)
    rt23h.check([("g_main_store", g, (c,), True), ("g_main_setattr", g, (d,), True)])
