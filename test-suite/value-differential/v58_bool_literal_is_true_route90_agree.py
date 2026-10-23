"""v58 AGREE — ROUTE #90's OVER-BREADTH CONTROL, in the corpus that re-measures itself.
The `Bool` LITERAL arm of route #42's whitelist is untouched by #90 and still PROVES.
`True is True` is True in CPython (the same singleton), so this returns 7 and the model
agrees. This is the AGREE direction that stops the gate being satisfiable by refusing
everything, and it independently re-confirms the repair did not narrow the whitelist to
nothing."""


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    if True is True:
        return 7
    return 0


if __name__ == "__main__":
    print(f())
