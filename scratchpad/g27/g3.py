r"""G3 — carrier of MY OWN #140 repair: the substitution covers PARAMETERS. A `raises`
condition over a FIELD (`self.tag`) names nothing in `param_names`, so `self.tag` is rendered
in the CALLER's scope — and a method caller has its own `self.tag`."""
_ = 0  # anchor


class H:
    tag: int

    def __init__(self) -> None:
        self.tag = -1

    #@ raises ValueError when self.tag < 0
    #@ assigns \nothing
    def f(self, k: int) -> int:
        if self.tag < 0:
            raise ValueError
        return k


class G:
    tag: int

    def __init__(self) -> None:
        self.tag = 5

    #@ requires self.tag >= 0
    #@ assigns \nothing
    #@ no_exception ValueError
    def caller(self, k: int) -> int:
        h = H()
        return h.f(k)
