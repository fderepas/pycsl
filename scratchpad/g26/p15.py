r"""P15 — #135/#134 WATCH: module-scope field store on a FRESH module-class instance
(a `collect_module_globals` object). #135 allows it by design; module code is not lowered."""
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == self.n
    #@ assigns \nothing
    def get(self) -> int:
        return self.n


g = C()
g.n = 5


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return g.get()
