# ROUTE #78 — A SEEDED `deque(...)` IS MODELLED AS EMPTY, AND EVERY ARGUMENT IS DISCARDED

**STATUS: FOUND AND REPRODUCED 2026-09-11 (gen #8). BOTH DIRECTIONS MEASURED. OPEN — repair
scoped below.**

**CLASS: the #69 class, the serious one** — a FALSE POSTCONDITION about ordinary, TOTAL Python.
No `no_exception`, no opt-in.

**HOW IT WAS FOUND: by the generator route #77 produced** — *a prose carve-out in the module
upstream of a guard is an unexploited route with a signpost on it.* A census of comments that
admit a construct is unmodelled/dropped/"a sound under-approximation" turned this up directly.

## THE EXPLOIT

```python
from collections import deque
#@ ensures \result == 0
def f() -> int:
    dq = deque([1, 2, 3])
    return len(dq)
```

    CPython:  3
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

## THE MECHANISM, AND THE FALSE SENTENCE THAT GUARDS IT

`src/pycsl/frontend/Module5_IREmitter.py` (~line 1275):

```python
if expr.func.id == "deque":
    # collections-plan: `deque(...)` reduces to the list/array model. Lower
    # it to an empty array literal so it reuses the append/index/len
    # machinery verbatim (identical to `dq = []`). A seeded iterable is
    # modelled as empty (sound under-approximation); left-end ops
    # (appendleft/popleft) and pop are out of scope.
    return {"type": "ArrayLit", "elts": []}
```

**`ArrayLit` with `elts: []` — every argument is discarded.** The justification in the comment
is the interesting part, and it is **FALSE**: *"a sound under-approximation"*. An EMPTY array is
not an under- or over-approximation of a three-element one; it is **a different concrete value**,
and the model then proves definite facts about it. Under-approximation would be a `val` with no
`ensures`; this is a literal.

**BANK THE SHAPE, NOT JUST THE BUG: "SOUND UNDER-APPROXIMATION" IS A CLAIM, AND IT IS CHECKABLE
IN ONE PROBE.** Any comment asserting that an erasure is sound should be treated as an unproven
lemma. Grep for the phrase; each hit is a candidate.

## BOTH DIRECTIONS, MEASURED

| driver | claim | CPython | PyCSL |
|--------|-------|---------|-------|
| `deque([1,2,3]); len(dq)` | `\result == 0` | **3** | **PROVED** ❌ |
| the TRUE twin | `\result == 3` | 3 | refused (Unknown) |
| `deque()` (EMPTY) — the **control** | `\result == 0` | 0 | PROVED ✅ faithful |

The empty-`deque()` control is what bounds the route: the repair must refuse only the **seeded**
form, exactly as `@dataclass` bounded route #76.

## BLAST RADIUS OF REFUSING THE SEEDED FORM: MEASURED AT ZERO

The only `deque(` in either verified corpus is `test-suite/corpus/pycsl-reference/0501.py:14`,
and it is `deque()` — the empty form, which stays faithful and must keep working. **The mirror
`src/self-annotate/` contains no `deque(` at all.** (The one seeded use in the tree,
`src/pycsl/frontend/pure_ast.py:2401` `todo = deque([node])`, is in the LIVE emitter and is
absent from the mirror, so it is not a verified artifact.)

## THE REPAIR, SCOPED

In `_py_expr_call`'s `deque` arm: if the call has ANY argument, raise a `PyCSLSemanticError`
naming the route; keep the existing empty-`ArrayLit` lowering for the zero-argument form. The
guard only RAISES or FALLS THROUGH, so it is byte-inert by construction.

**Cost note:** this is the same function/module as route #77's repair
(`frontend/Module5_IREmitter.py`, MIRRORED), so it owes a mirror sync + a whole-file
Module5_IREmitter re-proof — **but `_py_expr_call` must be checked for whether its mirror
counterpart is `\trusted`**; if it is, the body change is proof-free. Check before scoping.

## RESIDUE

The same comment admits a SECOND carve-out: *"left-end ops (appendleft/popleft) and pop are out
of scope."* **MEASURED: `deque(); dq.appendleft(7); len(dq)` claiming `\result == 0` is REFUSED
(Unknown)** — it fails closed today, but by an unrecognised-method fallback rather than by a
guard. **Reopening condition:** any change that gives `appendleft`/`popleft`/`pop` a recognizer
or a `writes` frame reopens it; re-probe `scratchpad/w58/c/k06_deque_appendleft.py`.

## WITNESSES

`scratchpad/w58/c/k01_deque_seeded.py`, `k01_twin.py`, `k05_deque_empty_faithful.py` (control),
`k06_deque_appendleft.py`, `k07_deque_seeded_index.py`, `k08_deque_seeded_requires.py`.
