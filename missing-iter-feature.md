# Missing feature — iterator semantics in PyCSL contracts

## The gap (worked example)

The autonomous stdlib annotator hit this during the
`itertools.cycle` promotion attempt:

> `cycle` has no documented preconditions (any iterable is
> valid, including empty), and the postcondition — "repeats
> the sequence indefinitely" — is an infinite-iterator semantic
> that lies outside the expressible contract surface. L3
> ceiling is correct here per Rule 4 / Part 3.

The agent emitted, correctly per the conventions doc:

```python
#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.cycle
# cite:_note: cycle returns an infinite iterator; iterator-sequence semantics
#             (indefinite cycling) cannot be expressed in the current contract
#             surface. Stub models existence of a return value only.
#@ ensures True
def cycle(iterable: int) -> int:
    return 0
```

This is the **L3 ceiling** for a whole class of stdlib
functions. Until PyCSL grows iterator semantics, none of them
can reach L4.

---

## Scope — what's gated by this gap

### Stdlib functions that are iterator-shaped

The current PyCSL stub set classifies these as `-> int`
placeholder returns:

**`itertools`** (12 functions in `src/pycsl_lib/itertools.py`):

| Function | Return shape | Currently |
|---|---|---|
| `count(start, step)` | infinite arithmetic sequence | int placeholder |
| `cycle(iterable)` | infinite cycling sequence | int placeholder |
| `repeat(object, times)` | finite or infinite single-value | int placeholder |
| `chain(*iterables)` | finite-or-infinite concatenation | int placeholder |
| `islice(iterable, *args)` | finite prefix/slice | int placeholder |
| `accumulate(iterable, func)` | finite running fold | int placeholder |
| `combinations(iterable, r)` | finite C(n,r) sequence | int placeholder |
| `permutations(iterable, r)` | finite P(n,r) sequence | int placeholder |
| `product(*iterables, repeat)` | finite cartesian product | int placeholder |
| `zip_longest(*iterables, fillvalue)` | finite max-length zip | int placeholder |
| `groupby(iterable, key)` | finite grouped sub-iterators | int placeholder |
| `starmap(func, iterable)` | finite mapped sequence | int placeholder |

**Builtins not yet stubbed but used in real code**:

| Function | Return shape |
|---|---|
| `iter(obj)` | iterator over obj's elements |
| `next(it[, default])` | one element or default |
| `enumerate(iterable, start)` | iterator of `(index, value)` pairs |
| `zip(*iterables)` | iterator of tuples |
| `map(func, *iterables)` | lazy mapped sequence |
| `filter(predicate, iterable)` | lazy filtered sequence |
| `reversed(seq)` | finite reverse iterator |

### Python-language constructs blocked by the gap

| Construct | Why it's gated |
|---|---|
| Generator functions (`yield`, `yield from`) | Return value is an iterator with author-defined element semantics. Currently auto-trusted. |
| Generator expressions (`(x for x in xs if p(x))`) | Same — anonymous iterator with predicate. |
| File iteration (`for line in f:`) | `f` is an iterator producing strings; element semantics depend on file contents. |
| `for x in <expr>:` where `<expr>` is an iterator (not a list) | Module 6 currently desugars only the `list` and `range(...)` shapes. Iterator shapes auto-trust the enclosing function. |
| `*` unpacking on an iterator (`a, *b = it`) | Element-by-element binding from an iterator with unknown length. |

### Quantitative impact

Of the ~1066 functions classified by `bin/stdlib-coverage-report.py`:

- `itertools`: 12 functions, all L2 → blocked from reaching L4 without iterator semantics.
- `collections.OrderedDict.{keys,values,items}`, `dict.{keys,values,items}` view objects: ~15 functions, iterator-shaped views.
- `re.finditer`, `re.split` (returns list), `csv.reader/writer`, `json.JSONEncoder.iterencode`: ~10 functions in other modules.
- Builtins (not yet stubbed): `iter`, `next`, `enumerate`, `zip`, `map`, `filter`, `reversed` — high-value, used in nearly every Python program.

**Estimated count gated by the gap: ~50–80 stub functions** (~5–8% of the total surface). Closing the gap raises the achievable L4+% ceiling proportionally.

---

## Design options

Four candidate models, ordered by expressive power (low → high) and implementation cost (low → high).

### Option A — Yield-set abstraction (low cost, lossy)

Model an iterator as the **set of values it can produce**, ignoring order and multiplicity.

New ghost type: `iterator` backed by a Why3 `set` (PyCSL already has `\set_*` operations via `ghost_set`). New contract atoms:

```python
#@ ensures \iter_yield_set(\result) == \set_of_array(iterable)
```

For `itertools.cycle(seq)`:

```python
#@ requires \length(iterable) >= 1
#@ ensures \iter_yield_set(\result) == \set_of_array(iterable)
#@ ensures not \iter_finite(\result)
```

**Pros**: cheap to add (reuse existing `ghost_set` machinery). Captures `for x in it: assert p(x)` style contracts ("every yielded element satisfies p").

**Cons**: loses ordering — can't express "the first element is `start`" or "the kth element is `start + k*step`". `accumulate`, `enumerate`, `zip` all degrade.

### Option B — Finite-prefix witness (medium cost, partial)

Augment Option A with a finite-prefix `ghost_list` that captures the first N elements (where N is a contract-level parameter). The iterator is `(yield_set, prefix : ghost_list, is_finite : bool)`.

```python
#@ ensures \iter_prefix(\result, 5) == [start, start+step, start+2*step, start+3*step, start+4*step]
#@ ensures not \iter_finite(\result)
```

**Pros**: captures sequencing for small prefixes (enough for "first element is X", "second element is Y"). Combines with Option A's yield-set for membership.

**Cons**: contracts get verbose. Need to pick a prefix length per call site. Doesn't capture arbitrary indexing.

### Option C — Coalgebraic stream (high cost, full sequencing)

Model iterators as WhyML lazy streams: `type stream 'a = Cons 'a (unit -> stream 'a) | Nil`. Add `\iter_head`, `\iter_tail`, `\iter_at(it, k)` atoms.

```python
#@ ensures \forall k: int. k >= 0 ==> \iter_at(\result, k) == start + k * step
#@ ensures not \iter_finite(\result)
```

For `itertools.cycle(seq)`:

```python
#@ ensures \forall k: int. k >= 0 ==> \iter_at(\result, k) == iterable[k mod \length(iterable)]
```

**Pros**: full sequencing semantics. Captures ordered, indexed, and infinite cases uniformly. Composes with `chain`, `zip`, `enumerate` cleanly.

**Cons**: WhyML streams are unfamiliar to SMT solvers. Quantifier-heavy contracts (∀k. ...) blow up Alt-Ergo. Requires meaningful tactical investment to make proofs go through.

### Option D — Generator desugar (high cost, intrusive)

Don't add a new type. Instead, at Module 5, **desugar** any function call returning an iterator into a `while True:` loop with explicit per-iteration ghost state. The iterator becomes implicit; only the loop body sees its elements.

**Pros**: re-uses existing loop verification machinery. No new ghost type.

**Cons**: huge Module 5 rewrite (every `for x in it:` becomes a generated loop). Hostile to user code (the desugared form bears little resemblance to the original). Cross-cuts the Module 5 → 6 boundary in load-bearing ways.

---

## Recommended design

**Option A (yield-set) as the first slice, with Option B's finite-prefix as a follow-up extension.**

Rationale:

1. **Pareto-optimal in cost vs. value.** A is ~1–2 weeks of work; covers `cycle`, `repeat`, `count`'s membership claim, `chain`, `filter`, the common `for x in it: <use x>` cases. Roughly 60% of the gated stub surface.
2. **Reuses existing machinery.** `ghost_set` already exists in `src/pycsl_lib` and the typed-ghost catalogue. The new `iterator` type is a structural sibling — same WhyML backend (`map int bool` for the underlying set), same emission pipeline.
3. **Soundness preserved by default.** A yield-set contract is *weaker* than the truth (it captures "elements come from this set" without ordering). Per the soundness>completeness rule (`docs/stdlib-global-plan.md` Part 3), weaker contracts never violate soundness — they just leave provability on the table.
4. **Option B is an additive extension.** Adding `\iter_prefix` later doesn't break Option-A-only contracts.
5. **Option C deferred.** Stream semantics are the "right" model but the cost is multi-week. Phase B in some future quarter.
6. **Option D rejected.** Module 5 desugar would touch too much load-bearing code with too little payoff.

### Concrete atoms (Option A)

New ghost type registered in `src/pycsl/module6_whyml/types.py` alongside `ghost_set`/`ghost_list`:

```python
"iterator": WhyMLType("iter int", initial="(empty_iter: iter int)", ref=False)
```

New contract atoms in the parser grammar (`src/pycsl/Module2_Parser.py`):

| Atom | WhyML lowering | Semantics |
|---|---|---|
| `\iter_yield_set(it)` | `Iter.yields it` | The set of elements `it` can produce |
| `\iter_finite(it)` | `Iter.is_finite it` | True iff `it` will eventually stop |
| `\iter_length(it)` | `Iter.length it` | Length when `\iter_finite(it)` (undefined otherwise) |
| `\iter_of_array(arr)` | `Iter.of_array arr` | Constructor from an array (helper for stub contracts) |
| `\iter_of_set(s)` | `Iter.of_set s` | Constructor from a `ghost_set` (lossy but convenient) |

### Worked example post-feature

```python
# itertools.cycle — at L4 after the feature lands
#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/itertools.html#itertools.cycle
#@ requires \length(iterable) >= 1
#@ ensures \iter_yield_set(\result) == \set_of_array(iterable)
#@ ensures not \iter_finite(\result)
def cycle(iterable: int) -> int:
    return 0
```

Caller side:

```python
# Reference test 0540 — cycle: caller asserts membership
# pycsl-expected: PASS
import itertools

#@ requires \length(arr) >= 1
#@ requires \forall i: int. 0 <= i and i < \length(arr) ==> arr[i] >= 0
#@ ensures \result >= 0  // any element of arr is >= 0, by membership
def first_from_cycle(arr: list) -> int:
    it = itertools.cycle(arr)
    return next(it)   // next() also needs a contract; see below
```

### `next()` and `for x in it:` contracts

Two derived primitives:

- **`next(it)`** — needs a stub:
  ```python
  #@ requires \iter_yield_set(it) != \set_empty
  #@ ensures \result \in \iter_yield_set(it)
  def next(it: int, default: int = 0) -> int:
      ...
  ```
- **`for x in it:`** — Module 6 emits an implicit `assume \iter_yield_set(it) != \set_empty` at loop entry + the loop body sees `x \in \iter_yield_set(it)` as a free fact.

---

## Implementation surface

### Phase 1 — Grammar + Module 4 (~3 days)

| File | Change |
|---|---|
| `src/pycsl/Module2_Parser.py` | Add `iter_yield_set`, `iter_finite`, `iter_length`, `iter_of_array`, `iter_of_set` as contract atoms in the EBNF. Mirror the existing `\set_*` atom pattern. |
| `src/pycsl/Module4_SemanticAnalyzer.py` | Recognize `iterator` as a valid ghost type tag (alongside `ghost_set` etc.). Type-check the new atoms (arg arity + return type). |
| `test-suite/annotations.md` | New §10.X subsection for iterator atoms. Numbered append-only. |
| `docs/pycsl-concrete-syntax-reference.md` | Add the new atom grammar productions. |
| `docs/pycsl-static-semantics-reference.md` | Inference rules for `\iter_*`. |

### Phase 2 — Module 6 emission (~4 days)

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/types.py` | Register the `iterator` ghost type. |
| `src/pycsl/module6_whyml/expressions.py` | Add `_handle_iter_yield_set`, `_handle_iter_finite`, etc. to `_EXPR_DISPATCH`. |
| `src/pycsl/module6_whyml/preamble.py` | Emit a Why3 `Iter` module declaration when any function uses an iterator atom. |
| `docs/pycsl-translational-reference.md` | Translation rules for each new atom. |
| New: WhyML `Iter` module under `data/why3_libs/` (or inline in the preamble emit) | Define `iter int` as `(set int, bool)` initially (Option A). Predicates `yields`, `is_finite`, constructor `of_array`, `of_set`. |

### Phase 3 — Stdlib stub refresh (~2 days)

| File | Change |
|---|---|
| `src/pycsl_lib/itertools.py` | All 12 functions: L2 → L4 with iterator-typed return + `\iter_*` ensures. |
| `src/pycsl_lib/builtins.py` (new or extend) | Stub `iter`, `next`, `enumerate`, `zip`, `map`, `filter`, `reversed`. |
| `test-suite/corpus/python-reference/stdlib/itertools/` | 24 reference tests (12 PASS + 12 NEG). |

### Phase 4 — Coverage classifier update (~1 day)

| File | Change |
|---|---|
| `bin/stdlib-coverage-report.py` | Recognize `\iter_*` atoms as "semantic" so iterator-shaped functions can reach L4 by Rule (b) of the L4 definition (cite + ensures). |
| `docs/stdlib-global-plan.md` Part 3 | Add a bridge: "When the docstring describes an iterator, use `\iter_yield_set`+`\iter_finite` to reach L4 instead of falling back to L3 ceiling." |

### Phase 5 — Optional follow-up: finite-prefix (Option B) (~3 days)

Adds `\iter_prefix(it, n)` returning a `ghost_list` of the first `n` elements. Lets `count(start, step)` express `\iter_prefix(\result, 1) == [start]` and lets `chain` capture order.

---

## Migration path

After Phase 1–3 land:

1. Coverage tool re-runs against the unchanged `itertools.py` stub: 12 functions still at L2 (no semantic content yet).
2. Edit `src/pycsl_lib/itertools.py` per the worked example. Each function moves L2 → L4.
3. Add 12 PASS + 12 NEG reference tests under
   `test-suite/corpus/python-reference/stdlib/itertools/`. Each function moves L4 → L5.
4. `bin/stdlib-coverage-report.py --module itertools` reports 12/12 = 100% L4+.
5. Overall L4+% rises from current ~6.8% to ~7.9% (12 functions × ~0.1%/function).
6. Repeat for builtins (`iter`, `next`, etc.) in `pycsl_lib/builtins.py`. Each adds another ~0.6%.

**Soundness regression check**: every L4 promotion adds a negative test under `test-suite/corpus/python-reference/stdlib/itertools/*_fails.py`. Run `bin/run-reference-tests.sh --start-at 1500 --stop-at 1550` to confirm they all exit `FAIL` under `--proof` mode.

---

## Effort estimate

| Phase | Effort | Cumulative |
|---|---|---|
| 1 — Grammar + Module 4 | 3 d | 3 d |
| 2 — Module 6 emission | 4 d | 7 d |
| 3 — Stdlib stub refresh + tests | 2 d | 9 d |
| 4 — Coverage classifier + bridge doc | 1 d | 10 d |
| 5 — Optional finite-prefix (Option B) | 3 d | 13 d |

**Phase 1–4 (Option A only): ~2 weeks**. Unblocks `itertools` (12 fns), builtins (7 fns), and the file-iteration / generator-expression paths. Yields a ~1.5–2% bump in overall L4+%.

**Phase 5 (Option B finite-prefix): ~3 days additional**. Modest additional value; defer unless `enumerate`, `zip`, or `count` callers actively need ordering claims.

---

## Risks + fallbacks

- **Quantifier explosion** in iterator contracts. Mitigation: keep contracts at the yield-set level (Option A) where possible. Defer ordered-sequence contracts (Option C-flavoured) to the finite-prefix extension.
- **WhyML `Iter` module needs careful design**. Risk: a chosen encoding becomes unworkable once richer contracts are tried. Mitigation: prototype the encoding against `itertools.cycle` and `itertools.count` BEFORE rolling it across all 12 functions. If the encoding doesn't carry, redesign in Phase 1, not Phase 3.
- **Negative tests for iterator preconditions** can be tricky. `cycle(empty)` is a runtime error in Python (Python 3.10+ — empty iterable produces an empty cycle, which is itself fine but `next()` on it raises `StopIteration`). The PyCSL stub `requires \length(iterable) >= 1` is a *spec choice*: model `cycle` as undefined on empty input. The negative test exercises this. Document the choice in the stub's `# cite:_note:`.
- **Builtin scope creep**. `iter`/`next`/`enumerate`/`zip`/`map`/`filter` are user-pervasive. Each needs a stub. Mitigation: deliver `itertools` first (10 functions, contained), then iterate on builtins separately.

---

## Out of scope (deferred)

- **Async iterators** (`async for`, `aiter`, `anext`). Their semantics combine iteration + coroutine state. Whole separate feature.
- **Generator `send()` / `throw()`** — coroutine-style two-way generators. Out of the iterator-as-pure-output abstraction.
- **`yield from` delegation semantics** — the recursive iterator-chaining shape. Could be modeled but adds complexity.
- **Iterator equality / inspection** (`id(it)`, `it is other_it`). Iterators are typically opaque references; PyCSL doesn't model object identity in the Hoare model.

---

## Suggested first PR

To prove the feature flies before committing the 2-week spend:

- Phase 1 grammar + Module 4 changes for **just `\iter_yield_set`** and **`\iter_finite`** (the two core atoms).
- Phase 2 Module 6 emission for the same two atoms.
- `src/pycsl_lib/itertools.py`: **only `cycle` and `count`** promoted to L4 (the two anchor examples in this doc).
- 4 reference tests (2 PASS + 2 NEG) under `test-suite/corpus/python-reference/stdlib/itertools/`.
- Coverage report shows `itertools: 2/12 = 16.7% L4+` (the ratchet starts ticking on the previously-blocked module).

Two-to-three-day deliverable. If this flies, commit to Phases 3–4 for the rest of `itertools` and the builtins.

---

## References

- [`docs/stdlib-global-plan.md`](docs/stdlib-global-plan.md) Part 3 — current "L3 ceiling" rule that this feature relaxes for the iterator subset.
- [`docs/stdlib-annotation-conventions.md`](docs/stdlib-annotation-conventions.md) §Translation Rules — Rule 4 (side effects) is the closest analog; iterator semantics deserve their own rule.
- [`src/pycsl_lib/itertools.py`](src/pycsl_lib/itertools.py) — the 12 functions blocked at L2 today.
- [`config/skills/pycsl-annotate/references/memory-model-extensions.md`](config/skills/pycsl-annotate/references/memory-model-extensions.md) §Typed ghost variables — the existing `ghost_set` / `ghost_list` machinery `\iter_*` will mirror.
- [`src/pycsl/module6_whyml/types.py`](src/pycsl/module6_whyml/types.py) — where the `iterator` ghost type will register.
- [`test-suite/annotations.md`](test-suite/annotations.md) §10 — where the new atom rows append.
- The agent log capture from 2026-05-31 13:47:22 that motivated this doc — `itertools.cycle` correctly stopped at L3 per the conventions; this feature is the path to lift it to L4.
