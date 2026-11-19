# ROUTE #97 — `--check-behavioral-subtyping` SILENTLY CHECKS NOTHING WHEN THE BASE CLASS
# HAS NO FIELDS: the override pair is never recorded, no refinement goal is emitted, and
# the file VERIFIES

**SEVERITY 2 (opt-in flag, but the flag's ENTIRE PURPOSE is the check it drops).
FOUND, REPRODUCED, MECHANISM PINNED IN THE IR, MINIMAL PAIR MEASURED, POSITIVE CONTROL
PROVING.** Found by the `continue`-census generator, from the handoff's own unprobed
candidate ("the Liskov goal dropped on a name miss"). **The candidate's stated mechanism was
WRONG and the route is real anyway** — it is not a name miss in `_emit_subtyping_goals`; the
pair never reaches that function.

## THE ONE-LINE STATEMENT

`Sub.f` overrides `Base.f` and STRENGTHENS its precondition — a textbook Liskov violation,
byte-for-byte the violation that corpus file **0445** exists to reject. If `Base` declares an
instance field, `--check-behavioral-subtyping` **FAILS** the file. If `Base` declares no
field, the same flag reports **`Verification SUCCESS! All contracts formally proven.`**

## THE MINIMAL PAIR — THEY DIFFER BY ONE `__init__` AND NOTHING ELSE

```python
class Base:                          #@ requires x >= 0   ensures \result >= x
    def f(self, x: int) -> int: ...
class Sub(Base):                     #@ requires x >= 5   ensures \result >= x   <-- STRENGTHENED
    def f(self, x: int) -> int: ...
```

| file | `Base` has a field? | refinement goals emitted | verdict under the flag |
|---|---|---|---|
| **H4** | **yes** (`self.v`) | **1** (`goal sub__f_refines_base`) | **FAILED** — violation caught |
| **H1** | no | **0** | **SUCCESS** — violation silently accepted |
| **H3** | no (but `Sub` has one) | **0** | **SUCCESS** — violation silently accepted |
| **H2** | yes, *and* `@staticmethod` | **1** | **FAILED** |
| **0445** (in-tree positive control) | yes | 1 | **FAILED** |
| **C2** — the `conforms_to` path, both classes fieldless | n/a | **1** (`goal c__f_refines_p`) | **FAILED** |

H2 and C2 are what make this precise. **`@staticmethod` was a red herring** — the first shape
that showed zero goals was a static override, and H2 refutes that reading: a static override of
a FIELDED base is caught. And C2 shows the sibling feature that shares the SAME `overrides` IR
list and the SAME goal emitter is IMMUNE. So the defect is neither "Liskov checking is broken"
nor "static methods are unchecked" — it is exactly **inheritance from a base class that has no
record**.

## THE MECHANISM, READ OFF THE IR (not inferred)

Instrumenting `apply_inheritance` from a wrapper (no source edit) gives the decisive evidence:

```
h4_plain_with_fields   TYPE_DECLS: [('Base','record',1,[]), ('Sub','record',0,['Base'])]
                       FUNCS: ['base__f', 'sub__f']
                       OVERRIDES: [{"sub_method":"sub__f","base_method":"base__f", ...}]

h1_plain_nofields      TYPE_DECLS: [('Sub','record',0,['Base'])]     <-- NO `Base` type_decl
                       FUNCS: ['base__f', 'sub__f']
                       OVERRIDES: []                                  <-- NEVER RECORDED
```

**Both functions exist in every case.** `base__f` and `sub__f` are in `FUNCS` in all three
files, so `_emit_subtyping_goals`' `by_name.get(...)` would resolve them perfectly. The pair
simply never arrives. The drop is upstream, in `ir_resolve.apply_inheritance`:

```python
records = {td["name"]: td for td in type_decls if td.get("kind") == "record"}
...
def merge_one(td):
    for bname in td["bases"]:
        base = records.get(bname)
        if base is None:
            continue                      # <-- HERE
        ...
        for fn in list(funcs):
            ...
            if tail in own_tails:
                ir_data.setdefault("overrides", []).append({...})   # the Liskov pair
...
for td in list(records.values()):         # <-- and the iteration is over RECORDS only
    merge_one(td)
```

A class with no instance fields gets **no `type_decl` at all**, so it is absent from `records`.

>>> **THIS IS THE `continue`-CENSUS SIGNATURE, VERBATIM: A LOOP THAT BOTH BUILDS SOMETHING AND
>>> ASSEMBLES A CHECKING POPULATION, WHERE A SKIP WRITTEN FOR THE BUILDING SILENTLY NARROWS THE
>>> CHECKING.** `if base is None: continue` is CORRECT for the job the loop was written for —
>>> merging fields, invariants, defaults and constants, of which a fieldless base has none. The
>>> same loop is the ONLY place the Liskov obligation is recorded, and for that job the skip
>>> deletes it. One line, two jobs, right for one of them. Routes #95 and #96 were the same
>>> shape; this is the third.

## WHY IT MATTERS MORE THAN "AN OPT-IN FLAG"

The drop lands precisely on **the stateless abstract base class** — the interface/pure-behaviour
base, which is the most common reason to write a base class at all, and the shape for which
substitutability reasoning is most obviously wanted. A user who turns the checker ON to police
their interface hierarchy gets a green, and the greener the hierarchy's design (no shared state),
the less of it is checked.

>>> **AN OBLIGATION THE EMITTER DROPS IS INDISTINGUISHABLE FROM ONE THAT WAS DISCHARGED**
>>> — route #93's lesson, now on the refinement VC. And the failure is INVERTED with respect to
>>> good practice: the cleaner the base class, the less checking it receives.

## STATUS

**OPEN.** Found, reproduced, mechanism pinned in the IR, minimal pair and positive controls
measured. Repair scoped below.

## THE REPAIR, SCOPED

Separate the two jobs the loop is doing. Record the override pairs for **every class that
declares bases**, independent of whether the base carries a record:

1. The pair recording must not sit behind `records.get(bname) is None`, and the driving
   iteration must cover classes with `bases` that are not in `records`.
2. Making this change ADDS obligations and never removes one, so it cannot be unsound — the
   worst case is a new unprovable goal on a genuinely non-refining override, which is the
   point.
3. **CO-LANDING, AND IT IS THE FAIL-CLOSED HALF:** `_emit_subtyping_goals`' own
   `if sub_fn and base_fn:` is STILL a silent drop for any pair it cannot resolve. Once pairs
   are recorded for bases that previously produced none, that lookup starts seeing inputs it
   never saw. It must become LOUD (a refusal) rather than silently emitting nothing — otherwise
   the repair only moves the silence one function downstream. Negative-test it by feeding it an
   unresolvable pair and checking it refuses.

**PREDICTED BLAST RADIUS — to be measured, not assumed:** only two corpus files use the flag
(0444, 0445) and **neither carries it in a `# pycsl-flags:` header**, so the byte-diff sweep
emits both WITHOUT goals and the repair should be byte-inert there. Both also have a FIELDED
base, so their behaviour should be unchanged even under the flag. Census the population of
`bases`-carrying classes with a fieldless base before landing.
