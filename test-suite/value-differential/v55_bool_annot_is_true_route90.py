"""v55 DISAGREE — ROUTE #90. `is True` on a `bool`-ANNOTATED param lowered to `x = 1`.
Route #42's whitelist admitted the operand because the symbol table said `bool`, and that
table is built from the ANNOTATION. `1 == True` is True so the int 1 meets the
precondition, but `1 is True` is False, so CPython returns 0 while the model proved 1."""


#@ requires x == 1
#@ ensures \result == 1
#@ assigns \nothing
def g(x: bool) -> int:
    if x is True:
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return g(1)


if __name__ == "__main__":
    print(f())
