r"""K3 — deferral census #3: the `-> str` / `return None` rule keys on the LITERAL; a `None`
returned through a local is a `Return` whose value is a Var."""
_ = 0  # anchor


class C:
    def pick(self, c: int) -> str:
        if c > 0:
            return "a"
        n = None
        return n

    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self, c: int) -> int:
        s = self.pick(c)
        if s is None:
            return 0
        return 7
