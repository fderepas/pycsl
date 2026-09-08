# OPEN ROUTE #54 — A DICT LITERAL'S EQUAL-BUT-DIFFERENTLY-SPELLED KEYS ARE COUNTED TWICE
# (found 2026-09-08 by relaunch #49 at `383ec4e5`)

## Three demonstrations, all `[+] Verification SUCCESS`, all false of the program

```python
#@ ensures \result == 2          # Python: len(d) is 1 — `True` hashes and compares equal to 1
def f() -> int:
    d = {1: 10, True: 20}
    return len(d)                            # scratchpad/w49/probeinv/d1.py

#@ ensures \result == 10         # Python: 20 — the second entry OVERWRITES the first
def f() -> int:
    d = {1: 10, True: 20}
    return d[1]                              # scratchpad/w49/probeinv/d2.py

#@ ensures \result == 2          # Python: 1 — "\x61" IS "a"
def f() -> int:
    d = {"a": 10, "\x61": 20}
    return len(d)                            # scratchpad/w49/probeinv/d4.py
```

## THE MECHANISM IS TWO MODELS OF ONE VALUE, AND THEY DISAGREE

The emitted body says it plainly:

```whyml
    let d = ref (map_update_some (map_update_some (const (None: option int)) 1 10) 1 20) in
    2                       (* <- `len(d)`, folded from the LITERAL's entry count *)
```

The MAP is right: two updates at the same key, the second wins, exactly Python. The
CONSTANT FOLD that answers `len(d)` and `d[1]` never consults it — it walks the literal's
syntactic entry list, counts the entries and returns the first whose key SOURCE matches. So
the two models of the same dict disagree wherever two keys are equal without being spelled
identically, and the fold is the one the contract sees.

The control that localises it: `{1: 10, 1: 20}` (literally identical keys) FOLDS TO 20 and
`d[1] == 10` fails closed (`d3.py`). The fold is not wrong about duplicates as such — it is
wrong about **Python equality**, which is what dict keys are compared by.

## WHY IT IS THE CAMPAIGN'S GENERAL SHAPE AGAIN

Route #48 was a SEEDED collection whose seed was dropped, and this is its mirror image: the
seed is kept in the map and DROPPED by the reader. Both are cases of a second, simpler model
answering a question the real model could have answered. The rule that would have caught
both: **a fold over a literal is only sound where the fold's key equality IS the model's key
equality.**

## REOPENING CAPABILITY

Two options, and the cheap one is honest:

1. **Fold only when the keys are provably pairwise distinct under PYTHON equality** — for
   literal keys that is decidable in the front end (normalise `True`/`1`, `1`/`1.0`, and
   string escapes before comparing) — and otherwise answer from the map (`Map` cardinality is
   not available in Why3, so `len` would have to be refused rather than folded).
2. Refuse the fold outright for a dict literal with more than one key and read everything
   from the map. Simpler, and it costs every corpus `len(<dict literal>)`.

CENSUS BEFORE BUILDING: a dict literal with two keys that are equal-but-differently-spelled
is pathological, so the population is expected to be zero — but the FOLD ITSELF is used by
every `len(<dict literal>)` and every `<dict literal>[k]` in the tree, so option (2)'s blast
radius is large and option (1)'s is zero. Measure both before choosing.
