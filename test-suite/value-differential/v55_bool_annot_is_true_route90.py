"""v55 DISAGREE — ROUTE #90. `is True` on a `bool`-ANNOTATED param lowered to `x = 1`.

Route #42's whitelist admitted the operand because the symbol table said `bool`, and that
table is built from the ANNOTATION, not from any enforcement. `1 == True` is True so the
int 1 MEETS the precondition, but `1 is True` is False, so CPython returns 0 while the
model proved 1. Deleted arm; now correctly refused.

SINGLE-FUNCTION on purpose: this plane requires exactly one module-level
`#@ ensures \result == <int>` line, so the cross-call escalation lives in corpus witness
1244 rather than here.
"""


#@ requires x == 1
#@ ensures \result == 1
#@ assigns \nothing
def f(x: bool) -> int:
    if x is True:
        return 1
    return 0


if __name__ == "__main__":
    print(f(1))
