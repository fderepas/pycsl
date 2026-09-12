# ROUTE #89 — A CONDITIONAL STORE TO A **COLLECTION** FIELD IS THE ARM ROUTE #83's REPAIR FENCED OFF, AND ROUTES #85/#87 MADE IT DECIDABLE

**STATUS: FOUND AND REPRODUCED 2026-09-12 (gen #11). BOTH DIRECTIONS MEASURED ON A LIST
FIELD AND A DICT FIELD.**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python.

## THE EXPLOIT

```python
from typing import List

class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self, k: int) -> None:
        self.xs = [1, 2]
        if k > 0:
            self.xs = [7, 8]

#@ ensures \result == 7
def f() -> int:
    c = C(0)            # the guard is FALSE, so the list is [1, 2]
    return c.xs[0]
```

    CPython:  1
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

The TRUE twin (`\result == 1`) is REFUSED. **THE MODEL TAKES THE CONDITIONAL STORE'S LITERAL
UNCONDITIONALLY** — the exact opposite of the pre-#83 defect, which took the straight-line
prefix unconditionally.

| carrier | shape | claim | CPython | PyCSL |
|---------|-------|-------|---------|-------|
| q4 | LIST field, guard FALSE (`C(0)`) | `\result == 7` | **1** | **PROVED** ❌ |
| q4 twin | same | `\result == 1` | 1 | refused |
| q5 | DICT field, guard FALSE (`C(0)`) | `c.d[1] == 9` | **5** | **PROVED** ❌ |
| q1 | LIST field, guard TRUE (`C(1)`) | `\result == 1` | 7 | refused ✔ |
| q1 twin | same | `\result == 7` | 7 | PROVED — right ANSWER, wrong REASON |

**q1's twin is the most instructive row in the table.** It PROVES and it is TRUE, but only by
coincidence: the model is not evaluating the guard, it is unconditionally preferring the
nested store. Change the actual argument from `C(1)` to `C(0)` and the same emission proves a
falsehood. **A DRIVER THAT PROVES A TRUE CLAIM IS NOT EVIDENCE THE MODEL IS FAITHFUL — IT CAN
BE THE SAME DEFECT SEEN FROM ITS LUCKY SIDE.**

## THE MECHANISM — A SOUNDNESS FENCE BUILT FOR SCALARS, AND TWO COMPLETENESS GAINS THAT WALKED PAST IT

Route #83 made a field stored inside control flow UNCONSTRAINED. Its emission site in
`module6_whyml/expressions.py` reads:

```python
        _unknown = set(rec_info.get("init_unknown_fields", []) or [])
        _NONSCALAR = ("list", "array", "dict", "set", "frozenset", "option")
        ... "(any int)" if (fn in _unknown and field_types.get(fn, "int") not in _NONSCALAR)
```

so **the fence covers SCALARS ONLY**. That was justified at the time — route #79's cost note
records that `_NONSCALAR` "already fenced the entire array arm", and the collection arms then
carried no decidable contents to be wrong about. **ROUTES #85 AND #87 CHANGED THAT.** They
made a dict/set/list field's literal contents FAITHFUL — a completeness gain — and in doing so
turned the unfenced arm from *imprecise* into *decidably wrong*, because
`_collect_class_fields` collects field literals with an `ast.walk` (so a NESTED store is seen
and, being later in the walk, WINS).

**>>> A COMPLETENESS GAIN CAN RE-ARM A SOUNDNESS DEFECT THAT AN EARLIER REPAIR HAD FENCED
OFF, WITHOUT TOUCHING EITHER OF THEM. <<<** #83's fence and #85/#87's captures are each
correct in isolation. The route lives in the fact that #83's fence was scoped by TYPE while
#85/#87 widened what a TYPE can decide. This is the generator-2 lesson one level up: a landed
repair is an instrument not only for finding a surviving carrier of ITS OWN defect, but for
re-testing every boundary some OTHER repair drew around the same field.

## THE PREDICTED REPAIR (not yet built)

Extend #83's `_unknown` override to the collection arms using the unconstrained values that
routes #86 and #87 already built and already spiked in Why3 — `any_map` (polymorphic, #86)
and `any_array` (polymorphic, #87). The fence becomes type-complete instead of scalar-only.
Cost is predicted small but MUST be measured, not predicted: the five real multi-store
`__init__` sites are `1209`/`1210` (route #83's own witnesses, scalar) and three in
`src/pycsl_lib` — `StringIO._size` (scalar), `Popen._pid` (scalar) and **`Sha256._input`,
which is a LIST field with exactly this shape** (`self._input = []` then `if data != 0:
self._input = data`). `src/pycsl_lib` is in NEITHER byte-diff corpus, so the gate that prices
it is the reference SUITE (route #83's lesson).

## WITNESSES

`scratchpad/w61/r89/q1_list_field_cond_store.py`, `q1t_…_twin.py`,
`q2_dict_field_cond_store.py`, `q3_list_field_only_nested.py`,
`q4_list_field_cond_false_branch.py`, `q4t_…_twin.py`, `q5_dict_field_cond_false_branch.py`.

**OWED:** re-reproduce q4/q5 at a tree WITHOUT the route-#88 repair (rule (p)). #88's three
edits are inert on this shape by inspection — Edit A fires only on a second TOP-LEVEL store,
Edit B only on a param-dependent capture, Edit C only on an `AugAssign` — but "by inspection"
is not a measurement, and the #88 byte-diff baseline worktree is the free place to do it.
