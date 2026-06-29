"""Witness driver — Pattern 2: `isinstance(x, T)` in non-ghost program context.

PyCSL already lowered `isinstance` in SPEC context (`requires isinstance(x, int)`)
to the `subtag (\typeof x) T` predicate. But in PROGRAM context
(`if isinstance(x, int): ...`) Why3 rejected the ghost `subtag` / `tag_*` logic
symbols ("Logical symbol subtag is used in a non-ghost context"), so any
`if isinstance(...)` body failed to prove.

Fix (expressions.py `_handle_isinstance`): in program (`not _in_spec`) context,
lower to a runtime int equality `(<value tag literal or typeof_op call> =
<T's tag literal>)` — a plain int `=` producing a bool accepted in `if`. Spec
context keeps the `subtag` predicate (carries the `object` base-type decision).
Additive: previously-failing program-context cases turn RED→GREEN; spec-context
and record-typed (`isinstance_op`) paths are byte-identical.
"""
#@ requires True
#@ ensures True
def if_isinstance_int(x) -> int:
    if isinstance(x, int):
        return 1
    return 0


#@ requires True
#@ ensures True
def if_isinstance_str(s) -> int:
    if isinstance(s, str):
        return 1
    return 0
