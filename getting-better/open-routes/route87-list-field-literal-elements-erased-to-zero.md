# ROUTE #87 — A LIST FIELD'S LITERAL KEEPS ITS LENGTH AND LOSES EVERY ELEMENT TO A DEFINITE `0`

**STATUS: FOUND AND **CLOSED AND FULLY GATED** 2026-09-12 (gen #10), FAITHFULLY. BOTH
DIRECTIONS MEASURED ON TWO CARRIERS.**

> ## CLOSING EVIDENCE
>
> | gate | verdict |
> |------|---------|
> | soundness planes | **34/34 green**, rc=0 |
> | IR conformance | **38/38 core + 38/38 front-end** — it FAILED first; the REPAIR was narrowed and NO golden was re-blessed |
> | byte-diff, pycsl-reference | 993 compared, **4 MOVED = exactly this route's own witnesses**, ZERO pre-existing files |
> | byte-diff, python-reference | **2203/2203 inert** |
> | byte-diff, MIRROR | **53/53 inert** |
> | fidelity | rc=0, 887 verbatim |
> | reference suite | **3350/3369, ZERO XPASS, rc=1**; failures 19 vs 19 BYTE-IDENTICAL |
>
> **THE CONFORMANCE FAILURE IS THE MOST INSTRUCTIVE PART.** The first build recorded every
> constant list literal in the IR; golden 0595 (`[0]*8`) gained a `field_list_literals` key
> while core-only conformance stayed 38/38 — the IR had moved for a file whose BEHAVIOUR had
> not. The gate was right, and it was pointing at an over-reach in the repair rather than at a
> stale golden. **CARRY INFORMATION IN THE IR ONLY WHEN IT CHANGES THE ANSWER.**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python.

## THE EXPLOIT

```python
from typing import List

class C:
    xs: List[int]
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs = [1, 2, 3]

#@ ensures \result == 0
def f() -> int:
    c = C()
    return c.xs[0]
```

    CPython:  1
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

The TRUE twin (`\result == 1`) was REFUSED.

## THE MECHANISM

`_field_default`'s list arm returns `(Array.make <len> 0)`. The LENGTH is captured (Module 5's
`_array_init_size` puts it in `field_defaults`) and **every ELEMENT is a definite zero**. So the
model is right about the shape and wrong about the contents — and `Array.make` makes the wrong
contents DECIDABLE rather than unknown, which is what turns an imprecision into a route.

| carrier | claim | CPython | PyCSL |
|---------|-------|---------|-------|
| element read `c.xs[0]` | `\result == 0` | **1** | **PROVED** ❌ |
| element read, TRUE twin | `\result == 1` | 1 | refused |
| **CROSS-CALL** — callee has `#@ requires xs[0] == 0` | `\result == 0` | **the program VIOLATES it** | **PROVED** ❌ |

## HOW IT WAS FOUND — THE GENERATOR, AND IT CAUGHT MY OWN CONTROL TABLE

**ROUTE #85's CONTROL TABLE, WRITTEN BY ME EARLIER THE SAME SESSION, RECORDS "a LIST field is
fail-closed".** That control ran exactly ONE operation — `len(c.xs)` — and the LENGTH *is*
faithful, so the control was true and useless as a general claim. Probing a SECOND operation on
the same carrier took two minutes and produced this route.

**A CONTROL IS A MEASUREMENT ABOUT THE OPERATION IT RAN, NEVER A THEOREM ABOUT THE TYPE.** This
is the generator route #81 was built on — it refuted route #59's "lists alias correctly" on
exactly this axis (#59 had measured an element STORE; the LENGTH-changing mutation was the
unmeasured one). **HERE IT IS THE MIRROR IMAGE: length right, elements wrong.** The pair is
worth remembering together, because between them they say that for a collection you must
ALWAYS probe both the shape and the contents — neither one implies the other, in either
direction.

**And the control that misled me was my own, written an hour earlier.** The rule is not "distrust
other generations' controls", it is "a control bounds the operation it ran".

## BLAST RADIUS — MEASURED, AND THIS ONE ACTUALLY TOUCHES THE CORPUS

    non-empty list literal -> field, in __init__ :  6 sites, ALL in test-suite/corpus
      all-int-constant (faithful arm)            :  5
      non-constant     (unconstrained arm)       :  1

Unlike routes #79, #83, #85 and #86 — every one of which was byte-inert — **this repair moves
corpus emissions**, so it had to be priced rather than predicted. The three REAL corpus files
affected (0595, 0596, 0704) all initialise with an ALL-ZERO literal (`[0]*8`, `[0]*4`), and the
other three (0980, 0981, 0993) are `pycsl-expected: FAIL` witnesses.

**SO THE EMISSION WAS DESIGNED TO MAKE THE COMMON CASE COINCIDE WITH THE EXISTING OUTPUT:** an
ALL-EQUAL literal emits the plain `(Array.make n v)` it already emitted, which for `v = 0` is the
IDENTICAL TEXT. Only genuinely non-uniform literals take the faithful
`let _alit = Array.make n (v0) in _alit[1] <- v1; … _alit` chain. **Designing the common case to
coincide with the existing output is cheaper than paying for it in the byte-diff** — and it is
not a trick, because `Array.make n v` IS the faithful lowering of a uniform literal.

## THE REPAIR

FAITHFUL where the literal is reconstructible — a LOCAL list literal has always lowered
faithfully to exactly this chain, so the information exists (route #82's rule), and the TRUE
claim now PROVES. A non-constant literal gets a POLYMORPHIC unconstrained array (`val any_array
(_u: unit) : array 'a`), polymorphic for the same reason as #86's `any_map`: the field may be
`array string` as easily as `array int`. Both forms were SPIKED in Why3 before being written —
the chain gives `Goal f'vc — Valid`, and `any_array` type-checks clean.

**NOTE A COMPLETENESS FACT THAT MAKES THE UNCONSTRAINED ARM CHEAP:** `len(c.xs)` on a field
array does not prove its true value even TODAY (measured: an empty list field cannot prove
`len == 0`), so the unconstrained arm gives up nothing that currently works.

## WITNESSES

`scratchpad/w60/r87/e1_elem.py`, `e1_twin.py`, `e3_crosscall.py`, `ctl_empty_list.py`,
`local_list.py` (the faithful local lowering the repair reuses).
