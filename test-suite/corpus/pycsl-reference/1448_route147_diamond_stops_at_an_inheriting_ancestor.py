r"""Test 1448 - ROUTE #147, CARRIER-RERUN on the repair's own second draft, a DIAMOND: `Dee(Bee, Cee)` over `Ay` with `Bee` declaring nothing and `Cee` declaring `afld + 100`. The C3 MRO is Dee, Bee, Cee, Ay, so Python calls Cee's - but draft 2 stopped at `Bee`, because the merge loop had ALREADY given `Bee` a COPY of `Ay`'s constructor. `Dee(7).get() == 7` PROVED while CPython gives 107. A COPIED-IN CONSTRUCTOR MAKES ITS HOLDER LOOK LIKE A DEFINER TO THE VERY LOOP THAT COPIED IT; an `init_inherits` ancestor is now walked THROUGH.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Ay:
    afld: int

    def __init__(self, afld: int) -> None:
        self.afld = afld

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


class Bee(Ay):
    pass


class Cee(Ay):
    def __init__(self, afld: int) -> None:
        self.afld = afld + 100


class Dee(Bee, Cee):
    pass


#@ ensures \result == 7
#@ assigns \nothing
def probe() -> int:
    o = Dee(7)
    return o.get()
