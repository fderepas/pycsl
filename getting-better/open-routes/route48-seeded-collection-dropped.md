# CLOSED — ROUTE #48 — CLOSED by relaunch #48 at `5342bea1`. Witnesses `pycsl-reference/1076`-`1079`.
#
# The entry below is kept VERBATIM as the record of how it was found, measured and
# scoped. Everything it says about the DEFECT still holds; everything it says about the
# route being open no longer does.

---

# OPEN ROUTE #48 — a SEEDED `Counter` / `OrderedDict` / `defaultdict` drops its seed, and
# the empty map's missing-key default is then DECIDED ON

**Found 2026-09-08 by relaunch #48, at commit `5aac69f2`, by reading the emitter's own
SOUNDNESS CLAIMS and probing each one.** The comment that named this route says:

> "a seeded iterable is modelled as empty (a sound under-approximation: content that
> depends on the seed fails to prove, never proves falsely)"

That is exactly the claim the measurement refutes.

## The demonstration (default `hoare` model, no flags, Python run to confirm)

```python
from collections import Counter

#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    c = Counter([1, 1, 2])
    if c[1] == 0:          # Python: c[1] is 2 -> f() returns 0
        return 7
    return 0
```
`[+] Verification SUCCESS! All contracts formally proven.`

| program | model | Python |
|---|---|---|
| `c = Counter([1,1,2]); if c[1] == 0:` | taken | `c[1]` is **2** |
| `d = OrderedDict([(1,5)]); if d[1] == 0:` | taken | `d[1]` is **5** |
| `d = defaultdict(int, {1:5}); if d[1] == 0:` | taken | `d[1]` is **5** |

Reproducers: `scratchpad/w48/probe/r3_counter_get.py`, `s5_ordereddict_seed.py`,
`s6_defaultdict_seed.py`.

## Why "never proves falsely" is wrong

`(const (None: option int))` is not an *unknown* map, it is the EMPTY map, and the model's
missing-key default is the integer `0`. So the seed is not merely lost — every read of a
seeded key becomes the decidable `0`, and a guard against `0` is decided the wrong way. This
is the campaign's general shape a SEVENTH time (routes #40 `...`, #41 erased locals, #42 the
bool singleton, #43 the complex literal, #44 `None`, #47 the `getattr` default): **a value
the model does not represent, lowered to an integer constant, is not lost but DECIDED.**

## What must NOT change, measured

| program | model | Python | verdict |
|---|---|---|---|
| `c = Counter(); if c[1] == 0:` | taken | `c[1]` is **0** | CORRECT — keep |
| `d = defaultdict(int); if d[9] == 0:` | taken | `d[9]` is **0** | CORRECT — keep |

An EMPTY `Counter` and a `defaultdict(int)` really do answer `0` for a missing key, and
`pycsl-reference/0498` is the driver that says so. The defect is confined to the SEED.

## THE FIX, and its blast radius is measured

Make the constructed map OPAQUE — `val function pycsl_seeded_map_<hash of the seed IR> : map
int (option int)`, with no defining axiom — for a construction that CARRIES a seed:
`Counter(x)`, `OrderedDict(x)`, `defaultdict(f, seed)`. Hash the seed's IR for the same
reason route #47 hashes the default's: two constructions from the same seed denote equal
maps and must stay provably equal, two from different seeds must not.

Leave the ONE-argument `defaultdict(f)` exactly as it is: its argument is the FACTORY, not a
seed, and the empty-map model is right for it.

CENSUS of the whole tree — `src/pycsl`, `src/self-annotate/src`, `src/pycsl_lib`, both
corpora: ELEVEN mentions, of which the only live constructions are two `defaultdict(list)`
in `src/pycsl/frontend/ir_resolve.py` (factory form, untouched by this fix), the corpus
driver `pycsl-reference/0498` (`defaultdict(int)`, factory form, untouched) and
`python-reference/stdlib/collections/counter_proves.py`, which is `#@ \trusted` under
`--no-proof`. **No live site carries a seed**, so the fix is byte-inert by measurement.

NOT CLOSED IN THIS INCREMENT because route #47 was already staged in the same file with its
mirror re-proofs unrun; stacking a third change on an unproven pair is how a window loses the
ability to say which change caused which failure.
