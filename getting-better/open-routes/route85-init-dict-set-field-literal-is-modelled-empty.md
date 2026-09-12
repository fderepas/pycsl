# ROUTE #85 — A NON-EMPTY DICT/SET LITERAL STORED TO A FIELD IN `__init__` IS MODELLED AS THE
# EMPTY MAP, AND MEMBERSHIP AND CONTENTS ARE THEN DECIDED ON

**STATUS: FOUND AND REPRODUCED 2026-09-12 (gen #10), AT HEAD. BOTH DIRECTIONS MEASURED ON
FOUR CARRIERS, WITH THREE CONTROLS THAT BOUND IT EXACTLY. OPEN.**

**CLASS: the #69 class, the serious one** — a FALSE POSTCONDITION about ordinary, TOTAL
Python. No `no_exception`, no opt-in, no decorator, no flag.

## THE EXPLOIT

```python
from typing import Dict

class C:
    d: Dict[int, int]
    #@ assigns self.d
    def __init__(self) -> None:
        self.d = {1: 5}

#@ ensures \result == 0
def f() -> int:
    c = C()
    if 1 in c.d:
        return 1
    return 0
```

    CPython:  1
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

The TRUE twin (`\result == 1`) is REFUSED. That asymmetry is what makes this a route rather
than imprecision: the model asserts a value it has no grounds for and refuses the value the
program actually computes.

## THE MECHANISM — SEEN DIRECTLY IN THE EMITTED WhyML, NOT INFERRED

`--keep-mlw` on the exploit gives, verbatim:

```whyml
  type c = { mutable d: map int (option int) }

  let f () : int
    ensures  { (result = 0) }
  =
    let c = { d = (const (None: option int)) } in
    ...
```

The field initialiser `{1: 5}` never reaches the record literal at all: the allocation site
emits **`const (None: option int)`, the TOTALLY EMPTY MAP**. `Map.get d 1` is then decidably
`None`, so `1 in c.d` is decidably FALSE and the emitter proves a definite false fact from it.
This is the SAME "an erasure to a DEFINITE value is dangerous, an erasure to an UNCONSTRAINED
value is merely incomplete" distinction the carve-out census ranks candidates by.

## FOUR CARRIERS, BOTH DIRECTIONS MEASURED

| carrier | claim | CPython | PyCSL |
|---------|-------|---------|-------|
| membership `1 in c.d` | `\result == 0` | **1** | **PROVED** ❌ |
| membership, TRUE twin | `\result == 1` | 1 | refused |
| **contents** `c.d.get(1, 0)` | `\result == 0` | **5** | **PROVED** ❌ |
| **SET field** `self.s = {7}`, `7 in c.s` | `\result == 0` | **1** | **PROVED** ❌ |
| **CROSS-CALL** — the empty map DISCHARGES a callee's `#@ requires 1 not in d` | `\result == 0` | **CPython VIOLATES that precondition** | **PROVED** ❌ |

**THE SECOND CARRIER IS THE SHARP ONE**: the model is wrong about the CONTENTS, not merely
about the length or the present-guard. **THE FOURTH IS THE SERIOUS ONE**: the defect CROSSES
THE CALL GRAPH — a stale empty map silently discharges a real precondition that the running
program violates, which is the same escalation routes #80, #82 and #83 each turned out to have.

## THREE CONTROLS, AND THEY BOUND IT EXACTLY

| control | behaviour | what it bounds |
|---------|-----------|----------------|
| `self.d = {}` (genuinely EMPTY literal), `1 in c.d` | `\result == 0` **PROVES — faithful** ✅ | the defect is "a NON-EMPTY literal is modelled empty", NOT "dict fields are broken" |
| `self.d = d` from a PARAMETER | **refused in BOTH directions** ✅ | fail-closed; the idiomatic constructor shape is NOT affected, and this is why the blast radius is 1 |
| `self.xs = [1, 2, 3]` (LIST field), `len(c.xs)` | **refused** ✅ | the list arm is fail-closed; this is a map/set defect |

The param control is the one that matters for scoping: it is what keeps this route small
rather than repository-wide.

## BLAST RADIUS — MEASURED

An AST census over `test-suite/corpus`, `src/self-annotate`, `src/pycsl` and `src/pycsl_lib`
for a NON-EMPTY dict/set literal stored to a `self.<field>` inside `__init__`
(`scratchpad/w60/r85_census.py`):

    sites: 1     — src/pycsl only
    corpus 0 · mirror 0 · src/pycsl_lib 0

**ZERO sites in the verified corpus and ZERO in the mirror**, so a repair is predicted
byte-inert over both corpora and to owe no whole-file re-proof — but that prediction is to be
CONFIRMED BY THE SWEEP, not relied on (route #83's blast radius was also entirely outside both
byte-diff corpora, and it was the reference suite, not the byte-diff, that actually priced it).

## HOW IT WAS FOUND — THE GENERATOR THAT PAID

Carve-out census candidate **5** (`map int (option int)` argument coercion substitutes
`(const None)`, the EMPTY map — `expressions.py:7396`), which had been ranked in the LOW-VALUE
TAIL and left unprobed by gen #9. The candidate's own carrier — the ARGUMENT-COERCION arm —
behaved as the candidate described (`(g (const (None: option int)))` is emitted verbatim for a
`self.<field>` actual) but was **NOT itself exploitable**, because the callee had no contract
relating its result to the map and so the caller learned nothing.

**THE ROUTE WAS FOUND IN THE SAME EMITTED FILE, ONE LINE ABOVE THE LINE THE CANDIDATE POINTED
AT.** Reading the `--keep-mlw` output to check whether the candidate's arm had fired at all
showed the record literal `{ d = (const (None: option int)) }` sitting right there — a SECOND,
independent erasure to the same empty-map constant, at the ALLOCATION site rather than the
call site, and that one is directly exploitable.

**THE LESSON, AND IT IS A NEW ONE FOR THE CAMPAIGN: WHEN YOU DUMP THE EMISSION TO CHECK
WHETHER A CANDIDATE'S ARM FIRED, READ THE WHOLE EMITTED FILE, NOT JUST THE LINE YOU CAME FOR.**
The verification step of a probe is itself a census over a small, fully-lowered program, and it
is the only artifact in the pipeline where every erasure is visible at once and in one place.
A candidate that is refuted can still be worth its cost by what its dump shows.

Corollary for the ranking: **candidate 5 was ranked LOW-VALUE TAIL and was right about the
mechanism, wrong about the exploitability, and led to a severity-1 route anyway.** The
carve-out census's hit rate (2 in 6 before this) should be re-read as 3 in 7, and the "low
value tail" label should not be trusted to mean "not worth a probe".

## WITNESSES

`scratchpad/w60/c5/b_direct.py` (exploit), `b_twin.py` (true twin, refused),
`scratchpad/w60/r85/c2_valueread.py` (contents), `c4_discharges_requires.py` (cross-call),
`c5_setfield.py` (set field), `ctl_empty.py` (the faithful empty control),
`c6_param_dict.py` (the fail-closed param control), `c3_listfield.py` (the fail-closed list control).
