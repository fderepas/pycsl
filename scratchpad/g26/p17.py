r"""P17 — module-scope store on a CLASS attribute (`C.N = 5`) shadowing a folded class constant."""
_ = 0  # anchor


class C:
    N = 3

    #@ ensures \result == 3
    #@ assigns \nothing
    def get(self) -> int:
        return self.N


C.N = 5


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    c = C()
    return c.get()
