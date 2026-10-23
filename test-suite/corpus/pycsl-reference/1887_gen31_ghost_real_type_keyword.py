r"""Test 1887 — gen #31 CONTROL for 1886 (expected PASS): a real ghost keyword still works.

Byte-identical to 1886 except that the declared type is one the emitter actually dispatches
on. The admissible set is the NINE of annotations.md §11.1 — `int`, `string`, `array`,
`ghost_dict`, `ghost_list`, `ghost_set`, `tuple2`, `tuple3`, `tuple4` — and NOT the twelve a
stale dataclass comment in `Module2_Parser` lists: the bare `list`, `set` and `dict`
spellings it names reach no branch in `statements.py` and would be silently `int` too, so
they are refused as well. Census: 53 `#@ ghost <n> : <t>` sites in the tree, every one
admissible, the bare spellings used nowhere.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires x > 0
#@ ensures \result == x
#@ assigns \nothing
def f(x: int) -> int:
    #@ ghost g : ghost_dict = \empty_map
    return x
