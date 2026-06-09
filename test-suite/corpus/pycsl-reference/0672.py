"""Test 0672 — negative: `\length` on a dict in a SUBSCRIPT-ghost (`g[i] = …`).

`_validate_predicate_bases` fires inside a `#@ ghost g[i] = …` (GhostArraySet) — the
error context is `function 'f' (ghost 'g[...]')`, distinct from the simple-ghost form
(0669, `(ghost 'g')`). The B4 IR migration must reproduce this fourth surface context.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def f(d: dict, g: list) -> int:
    #@ ghost g[0] = \length(d)
    return 0
