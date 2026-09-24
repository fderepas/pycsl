# ROUTE #225 (#49, gen #31) — a function returning `[]` PROVES `\length(\result) == 1024`

**STATUS: LIVE SEV-1. A FALSE POSTCONDITION IS CERTIFIED.** Not a completeness gap, not a
refusal: the verifier reports `Verification SUCCESS` for a contract clause that CPython
contradicts on every run.

## The witness

```python
#@ ensures \length(\result) == 1024
#@ assigns \nothing
def mk() -> list:
    return []
```

    [+] Verification SUCCESS! All contracts formally proven.

Python: `len(mk())` is `0`. The TRUE clause is refused:

```python
#@ ensures \length(\result) == 0      # -> Prover result is: Unknown. FAILS.
```

Both halves hold for the indirect shape too (`xs = []` then `return xs`): the false claim
proves, the true one does not.

## The mechanism

`[]` lowers to `(Array.make 1024 0)` — the emitter's "no elements" stand-in (wall-lesson
(ao)). A Why3 `array` has an immutable length, so the model of the empty list has length
**1024**, and `Array.length result = 1024` is simply true of the emitted term.

## Why the existing repair does not cover it

Route #159 already found this mechanism for a LOCAL and repaired it, in `pycsl.py`, on the
emitted TEXT: inside a `let X = (Array.make 1024 0) in` scope with no `X_len` sidecar,
`in_bounds ((Array.length X))` is rewritten to `in_bounds (0)`. Measured today, the local
path is indeed faithful — `xs = []; return len(xs)` proves `\result == 0` and refuses
`\result == 1024`.

The repair is scoped to ONE obligation (`in_bounds`) in ONE syntactic scope (a `let`
binding of the placeholder). It does not reach:

  * a `\length(\result)` clause on a function that RETURNS the placeholder, which is the
    witness above — and this is the shape that crosses a module boundary;
  * any other contract clause quantifying over the array's length.

**THE CROSS-FUNCTION CONSEQUENCE IS THE SERIOUS ONE.** A caller consuming `mk`'s contract
assumes `Array.length result = 1024` of a list CPython says is empty. When the caller then
learns the true length from elsewhere, the assumption set is CONTRADICTORY and every
downstream goal is vacuously provable. That is precisely the modular false-green recorded
in `getting-better/20260718-0633-stmt-list-append-mutation-wall-response.md` ("`driver`
returns the literal `0` yet `ensures result = 1` proves Valid … the assumption is
`1024 = 1` → false → every downstream goal is vacuously provable"), and `--check-vacuity`
did not flag that one either.

## Shape of the repair (not yet built)

The honest fix is to stop lying about the length rather than to patch each consumer:
`[]` is an empty list and its faithful model has length 0. Everything that made 1024 look
necessary — append targets, slice writes — already carries its own machinery (a `ref Seq`,
an `X_len` sidecar), and the #159 hack is itself an emulation of "the length is really 0".
Candidate: emit the genuine empty literal as a length-0 array, keeping `(Array.make 1024 0)`
only where it is an ERASURE stand-in for a list the model does not represent — the two uses
are currently spelled the same, which is the deeper defect.

GATE BEFORE ANY OF IT: this touches a literal that appears throughout both corpora, so the
corpus byte-diff comes first and the population of changed files is the measurement that
decides the shape.

Measured 2026-09-24. Witnesses: `$SCRATCH/g31/orl/{g,h,i,j,k}.py`.

---

## CLOSED (2026-09-24, gen #31) — the consequence is corrected; the literal is not

| shape | claim | before | after |
|---|---|---|---|
| `return []` | `\length(\result) == 1024` | **SUCCESS (false)** | FAILED |
| `return []` | `\length(\result) == 0` | Unknown (refused) | **SUCCESS** |
| `xs = []; return xs` | `== 1024` | **SUCCESS (false)** | FAILED |
| `xs = []; return xs` | `== 0` | Unknown | **SUCCESS** |
| `xs = []; xs.append(7); return xs` | `== 1` | SUCCESS | SUCCESS (unmoved) |
| the same | `== 0` / `== 1024` | FAILED | FAILED (unmoved) |

A model that REFUSES THE TRUTH and CERTIFIES THE LIE is the same defect seen from both
sides, and both sides moved.

The repair is in `_run_pipeline`'s post-emission pass, beside route #159's, and in its
idiom: when a function's FINAL expression is the placeholder itself — or a local bound
ONCE to it with no `_len` sidecar, no element store and no rebinding — the `(Array.length
result)` in that function's contract becomes `(0)`. **Strictly stronger, so no proof can
become easier**: 0 is both the true length and the smallest one. A function that returns the
placeholder on only one branch ends in a `try`/`Return` form, does not match, and is left
alone — fail-closed.

Corpus witnesses `1869` (the false twin, FAIL), `1870` (the true claim, PASS, both
spellings) and `1871` (the append path, PASS — the BOUND, which should be the first file to
go red if a future attempt moves the literal itself).

### STILL OPEN — the named capability, and why it was not taken here

`Array.make 1024 0` is spelled the same for TWO jobs:

  * the CAPACITY of an append target, whose real length is carried by an `X_len` sidecar
    (`statements.py:7376` emits `let <tgt> = Array.make 1024 0 in` for exactly that);
  * the VALUE of an empty list that is never appended to.

A Why3 array's length IS its capacity, so ONE literal cannot serve both, and changing it at
the producer (`expressions.py:18087`, the only producer of this string) breaks the first
job. Separating the two — a marked empty-list VALUE emitted at length 0, the capacity
placeholder left alone — is the real repair and remains open. `1871` is its guard.

Worth recording about the population: the empty `ArrayLit` node has exactly ONE other
producer, `deque()` with no arguments, and that one really IS empty (the SEEDED form is
already refused by route #78). So the node is never an erasure stand-in — which is what
makes the length-0 model correct and the separation a mechanical job rather than a
judgement call.

### THE GUARD THAT THE FIRST VERSION DID NOT HAVE

Excluding element stores, `_len` sidecars and rebindings is NOT enough to know a local is
still empty at the return: it can be handed to a CALLEE that appends to it.

```python
def mk() -> list:
    ys = []
    fill(ys)        # \trusted, appends
    return ys
```

Claiming 0 there would swap one false length for another, and the new one is WORSE, because
0 is the PROVABLE direction — `\length(\result) == 0` would verify for a list Python says
is non-empty. The guard is therefore an OCCURRENCE COUNT: the name must appear EXACTLY
TWICE in the emitted body, its binding and the final expression. Anything that so much as
mentions it elsewhere is left alone. Measured: the shape above does not verify `== 0`.

### THE CAPABILITY, WITH ITS SITES — separate the CAPACITY from the VALUE

Measured while the repair above was being gated, so the next attempt does not have to
re-find them:

| site | job today | after the split |
|---|---|---|
| `module6_whyml/expressions.py:18087` — `return "(Array.make 1024 0)"`, the ONLY producer of this string, reached for an `ArrayLit` with no `elts` | the empty-list VALUE | `(Array.make 0 0)` — the faithful length |
| `module6_whyml/statements.py:7376` — `let {safe_tgt} = Array.make 1024 0 in`, emitted for each `append_targets` name alongside `let {safe_tgt}_len = ref …` | the CAPACITY of a growable local, whose real length is the `_len` sidecar | unchanged at 1024 |

The two are ALREADY emitted by different code paths, and the append-target set is already
computed — so the split is a change of one literal plus the consumer guards, not a new
analysis. That is the whole reason it is worth doing rather than patching more consequences.

CONSUMERS THAT COMPARE AGAINST THE EXACT STRING and must learn the new spelling (all
`== "(Array.make 1024 0)"` or `.strip() == …` tests): `expressions.py` 7151, 8037, 8054,
8086, 9677, 12835, 12855, 12878, 14576; `statements.py` 2165; `types.py` 280. Each is a
"this argument is the empty-list placeholder" test, so each wants the VALUE spelling.

WHAT WILL BREAK FIRST IF THE SPLIT IS DONE CARELESSLY: an append emitted as
`arr[!arr_len] <- v` against a length-0 array is out of bounds, so corpus `1871` goes red.
That file exists for exactly this.

AND WHAT IT UNBLOCKS: the `or []` conversion family (54 `\trusted` stubs, the largest
identified in the backlog), which is blocked on BOTH of the empty literal's other defects —
it ALLOCATES, so a value-position `A or []` fails in a pure function ("this function has
side effects, it cannot be used as pure") and in a method (Why3 region analysis: "this
expression prohibits further usage of the variable ys"). The working lowering is parked at
`$SCRATCH/g31/or_empty_list.patch`.

### THE SIBLINGS WERE PROBED, AND THE LITERAL IS THE ONLY CARRIER

A false length is only interesting if the family is wider than one spelling, so every other
way to produce an empty collection was tried against the same pair of claims
(`\length(\result) == 1024`, the lie, and `== 0`, the truth):

| expression | `== 1024` | `== 0` |
|---|---|---|
| `return []` (before the repair) | **SUCCESS** | Unknown |
| `return bytes()` | FAILED | SUCCESS |
| `return bytearray()` | FAILED | SUCCESS |
| `return [0] * 0` | FAILED | SUCCESS |
| `return tuple()` | FAILED | FAILED (completeness gap, not a carrier) |
| `x = []; x.append(7); return x` | FAILED | FAILED (`== 1` SUCCEEDS — faithful) |
| a list FIELD initialised to `[]` (class invariant) | — | SUCCESS (witness is `Array.make 0 0`) |

Three of those paths already write the FAITHFUL length, and one of them — the class-field
initialiser — spells it `(Array.make 0 0)` in the very same emitter. So the defect was one
literal out of step with its own siblings, not a model-wide choice.

The ARGUMENT direction was checked too and is fail-closed both ways: a callee whose
`#@ requires \length(xs) == 1024` is handed `[]` does NOT discharge, and one requiring
`== 0` does.

### THIS IS THE THIRD POSITION OF ONE MECHANISM, AND THE OTHER TWO ARE ALREADY CLOSED

| position | route | repair |
|---|---|---|
| INDEXING inside a local's scope | #159 (gen #29) | post-emission: `in_bounds ((Array.length X))` -> `in_bounds (0)` |
| the ARGUMENT at a call boundary | #196 (gen #30) | `expressions.py:8102` substitutes `(Array.make 0 0)` for the exact placeholder at an `array int` param |
| the RETURN across a function boundary | **this one** (gen #31) | post-emission: the contract's `(Array.length result)` -> `(0)` |

Route #196's own comment says it: *"The faithful value is the genuinely EMPTY array — `[]`
really does have length 0"*, and its witness 1689 is the argument-shaped twin of 1869. So
the emitter ALREADY writes `(Array.make 0 0)` for this literal in one place, and the class
field initialiser writes it in another. **Three positions, three separate patches, one
literal that is wrong at the source** — which is the whole argument for doing the producer
split next rather than waiting for a fourth position to be found.

What made #196 stop at the boundary rather than fix the producer is exactly what makes the
split non-trivial: the same literal is also the CAPACITY of an append target. Neither #159
nor #196 could change it without breaking that, and neither says so — this finding is where
that constraint is written down.

### THE CENSUS CAUGHT A REGRESSION IN THE REPAIR ITSELF

Counting the placeholder in the freshly emitted corpus (20 of 1354 files, 25 occurrences,
ZERO in python-reference) turned up its contexts:

```
   7  let xs = (Array.make 1024 0) in
   5  by { disk = (Array.make 1024 0) }
   4  let d : disk = { disk = (Array.make 1024 0) }
   4  let a = (Array.make 1024 0) in
   3  by { balance = (Array.make 5 0); audit = (Array.make 1024 0); audit_len = 0 }
   2  (Array.make 1024 0)
```

and the third and fifth rows are the problem: **`[0] * 1024` emits the SAME TEXT as `[]`.**
A field named `disk` initialised to 1024 zeroes really is 1024 long, and the `audit` row
carries an `audit_len` sidecar, i.e. it is the CAPACITY use.

So the post-emission rewrite, which keys on the text, mis-fires:

```python
#@ ensures \length(\result) == 1024
def mk() -> list:
    return [0] * 1024          # TRUE — and it stopped proving
```

Not unsound (it makes a true claim unprovable, the safe direction) but a real completeness
regression, and invisible to the corpus byte-diff precisely because no corpus file happens
to return a 1024-element literal from a function with a `\length(\result)` contract. **The
census found what the byte-diff could not**, which is the argument for doing both.

FIX: the rewrite is narrowed by an IR-LEVEL FILTER. `_run_pipeline` holds `ir_data`, so the
set of functions whose final statement returns an EMPTY `ArrayLit` — directly, or through a
local bound once to one — is computable exactly, and only those functions' contracts are
touched. Text decides nothing on its own any more; it only locates the block for a function
the IR has already named. The filter can only REDUCE firing, so the byte-inert corpus
measurement above still stands.

### WHAT THE 25 CORPUS OCCURRENCES ACTUALLY ARE (data for the split)

Read in the fresh emission, so the next attempt starts with the population classified:

  * `1536` / `1538` / `1541` and siblings — the route #158/#159 witnesses: an empty-literal
    LOCAL with NO `_len` sidecar, indexed or stored into. `1538`'s `in_bounds (0) (0)` is
    #159's own rewrite already in place. Under a length-0 literal these keep failing, for
    the right reason (`xs[0]` on an empty list really is out of bounds), so the split is
    expected to leave their verdicts alone.
  * `{ disk = (Array.make 1024 0) }` / `by { disk = … }` — a REAL 1024-element literal
    (`[0] * 1024`). These must NOT move: the length is correct.
  * `by { … audit = (Array.make 1024 0); audit_len = 0 }` — the CAPACITY use, sidecar and
    all. These must NOT move either.

So of the three context families, only the FIRST is the empty-list VALUE, and the split has
to be made at the producer with the append-target set in hand — not on the text, which
cannot tell the three apart. That is the whole content of the capability.
