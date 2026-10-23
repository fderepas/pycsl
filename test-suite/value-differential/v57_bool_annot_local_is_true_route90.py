"""v57 DISAGREE — ROUTE #90, the ANNOTATED LOCAL. The deleted arm keyed on the symbol
table, which carries annotated LOCALS as well as params, so `y: bool = 1` took it too.
`1 is True` is False, so CPython returns 0 while the model proved 1. This driver is the
one that would catch a repair scoped to parameters only."""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    y: bool = 1
    if y is True:
        return 1
    return 0


if __name__ == "__main__":
    print(f())
