"""Test 1038 — ROUTE #40 negative witness (c): `<int> is ...` was DECIDABLY TRUE.

FALSE OF THE PROGRAM: `0 is Ellipsis` is False, so Python returns 0.

The mirror direction of 1037: here the integer is the bound name and `...` is the
literal. Module 5 lowers `ast.Is` to `==` and the `...` to the literal 0, so the
guard read `0 = 0`. At the parent commit b5fb0688 `\result == 7` PROVED.

This shape is why the fix had to be an OPAQUE VALUE rather than a refusal keyed on
"`...` in a value position": the two CONCRETE mirror methods that use `...`
(`pure_ast._Unparser.visit_Constant`, `pure_ast.atom`) use it in exactly this
comparison position, and no syntactic test separates them from this exploit. Opacity
closes both at once — the mirror's `value is ...` becomes `!value = pycsl_ellipsis`,
which is MORE faithful than `!value = 0` and still undecidable.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 0
    if x is ...:
        return 7
    return 0
