r"""Test 1918 — gen #33 (expected PASS): two string LITERALS concatenated, alone.

THE ABSENCE OF THIS FOUR-LINE TEST IS WHY THE BUG SURVIVED. Before the fix, this exact
program emitted

    val str_concat_op (a: string) (b: string) : string
      ensures { result = (concat a b) }

into a preamble whose `use` list was only `int.Int` / `int.EuclideanDivision` / `ref.Ref`,
and L3-tc rejected it: **unbound function or predicate symbol 'concat'**. `concat` comes
from `string.String`.

WHY THE FLAG MISSED IT. `needs_string` is computed from the IR — a ghost `string`, a `str`
in a symbol table, a `str` return annotation, a `seq string` — and it is computed BEFORE any
function body is emitted, so it cannot see an op a body registers later. None of its
disjuncts fires for a local bound to two string literals. The op's TYPE needs only `string`;
only its ENSURES needs `concat`.

>>> A DECLARATION'S CONTRACT IS PART OF ITS DEPENDENCIES. A dependency derived from the op's
>>> SIGNATURE, or from a feature flag over the IR, cannot see a symbol that only the
>>> `ensures` mentions.

This is the STRING TWIN of route #44's `use array.Array` pull, which fixed the identical
defect for `array` in the same method and left `string` unfixed. The repair sits beside it.

THE CONTROL IS 1919: `x + "b"` — a str PARAM and a literal — which always worked and emits no
`str_concat_op` at all. Keeping both is the point: the bug lives in the difference between
them, so a test of either one alone would have missed it, and did.

The postcondition is deliberately SHARP rather than merely true: `\result == 2` holds only if
the length law on the concatenation is actually modelled, so this file would fail if the op
were declared without its `ensures`.
"""
# pycsl-expected: PASS


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    s = "a" + "b"
    return len(s)
