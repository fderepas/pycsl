# Memory Model for Array Aliasing in PyCSL

## The Aliasing Problem in Formal Verification

This is one of the deepest problems in program verification. The case where two array
parameters might point to the same memory location is called **heap aliasing**, and it
breaks the standard model PyCSL currently uses.

---

*See also: [Why Approach 3 Was Omitted — Heap Threading vs Frama-C](#approach-3-explicit-heap-threading-in-detail)*

---

## Current Model (No Aliasing)

PyCSL's array model is **value-semantic**: each `array int` parameter is treated as an
independent chunk of memory. `arr[i] <- v` mutates `arr` but nothing else. Why3's
`array.Array` theory implicitly assumes this.

---

## The Problem

```python
def fill(list_a: list, list_b: list, n: int) -> int:
    list_a[0] = 42
    return list_b[0]   # could be 42 if list_a is list_b!
```

The postcondition `\result == list_b[0]` is ambiguous. If `list_a is list_b`, the answer
is `42`. If not, it's whatever was there before.

---

## The Memory Model: Separation Logic / Region-Based Heap

The standard solution is to move from **value semantics** to a **heap + reference
semantics** model.

### Core idea: the heap is a single global map

```
heap : Loc → int
```

Arrays are not values — they are **references** (locations into the heap):

```
list_a : Loc     (* a pointer, not an array value *)
list_b : Loc
```

`list_a[i]` becomes `heap[list_a + i]`, and mutation `list_a[i] <- v` becomes
`heap := heap[list_a + i ← v]`.

Now `list_a is list_b` is expressible as `list_a = list_b` (pointer equality), and the
aliased mutation is correctly modelled: updating `heap[list_a + 0]` also changes
`heap[list_b + 0]` when `list_a = list_b`.

---

## Three Approaches

### 1. Explicit Non-Aliasing Precondition (Simplest, Pragmatic)

Add a contract precondition asserting the arrays are **disjoint**:

```python
#@ requires list_a != list_b          (* pointer inequality *)
#@ requires list_a + n <= list_b or list_b + n <= list_a  (* regions don't overlap *)
```

This is what C's `restrict` keyword does. It doesn't model aliasing — it **rules it
out**. This is the practical choice for most algorithms.

### 2. Separation Logic (Clean, Compositional)

Replace Hoare triples `{P} S {Q}` with **separation logic triples** `{P} S {Q}` where
`P` is a *separating conjunction* (`*`):

```
{list_a ↦ _ * list_b ↦ _} fill(list_a, list_b, n) {list_a ↦ 42 * list_b ↦ \old(list_b[0])}
```

The `*` ("star") means the two heap regions are **disjoint by construction** — you can't
even form the triple if they alias. Why3's `why3-sep` library or Iris (in Coq) implement
this. This is the cleanest approach but requires rewriting the entire contract language.

### 3. Explicit Heap Threading (What Why3 can do today)

Thread the heap as an explicit ghost parameter:

```whyml
val fill (h: heap) (a b: Loc) (n: int) : heap
  requires { valid h a n }
  requires { valid h b n }
  ensures  { result = h[a + 0 <- 42] }
  (* when a = b, this also implies result[b+0] = 42 *)
```

The heap is a first-class value passed in and out. Aliasing is handled automatically
because both `a` and `b` index into the same `result` heap.

---

## What This Would Cost PyCSL

| Aspect | Current | With Heap Model |
|---|---|---|
| Array type | `array int` | `Loc` (pointer) + `heap: Loc → int` |
| Read `arr[i]` | `arr[i]` | `heap[arr + i]` |
| Write `arr[i] = v` | `arr[i] <- v` | `heap <- heap[arr+i ← v]` |
| Contract language | `\forall i; arr[i] >= 0` | `\forall i; heap[arr+i] >= 0` |
| Non-aliasing | implicit | explicit `requires arr1 != arr2` or `*` |
| Module 6 | emits `array.Array` | emits `map.Map` + `Loc` type |
| Annotation effort | low | high — LLM must reason about pointers |

---

## Recommendation

For PyCSL's use case, **Approach 1** (explicit non-aliasing precondition) is the right
pragmatic choice:

```python
#@ requires list_a != list_b
```

Add a `Loc` type alias and pointer-inequality to Module 2's grammar. This is a single
contract rule with no model change. Full separation logic (Approach 2) is academically
correct but would require redesigning the entire contract language and annotation workflow.

Approach 3 is omitted from this recommendation because, while correct, it imposes a very
high annotation and proof cost — see the detailed analysis below.

---

## Why Approach 3 Was Omitted — and What It Actually Offers

### The Gap in the Recommendation

Approach 3 (Explicit Heap Threading) was omitted because it was presented as a
*middle-ground* option — more expressive than Approach 1 but less principled than
Approach 2. However, this undersells it. Approach 3 is in fact the closest analogue to
how **Frama-C** models heap memory, and it deserves a serious comparison.

---

## Approach 3: Explicit Heap Threading in Detail

The idea is that the heap is a **first-class value** — a ghost parameter passed in and
returned:

```whyml
type heap = { contents: map Loc int }

val fill (h: heap) (a b: Loc) (n: int) : heap
  requires { valid h a n }
  requires { valid h b n }
  ensures  { forall i. 0 <= i < n -> result.contents[a + i] = h.contents[a + i] }
  ensures  { result.contents[a + 0] = 42 }
  (* aliasing case: if a = b, then result.contents[b + 0] = 42 follows for free *)
```

The heap flows through the program like water through pipes. Every function that touches
memory takes a `heap` in and returns a (possibly updated) `heap` out. Aliasing is
modelled correctly because `a` and `b` are just integer offsets into the same map.

This is **purely functional reasoning about an imperative program** — a classic technique
in denotational semantics (Reynolds 1978, formalised in separation logic by O'Hearn &
Pym 1999).

---

## Frama-C's Memory Model

Frama-C's WP (Weakest Precondition) plugin uses a fundamentally different but related
approach. It does **not** thread the heap explicitly through function signatures.
Instead:

### 1. The Heap Is Global and Implicit

Frama-C models C memory as a collection of **typed memory stores** (one per C type),
maintained as ghost global state:

```
int_store   : Loc → int
float_store : Loc → float
ptr_store   : Loc → Loc
```

Each store is a global logical map. A C statement `*p = 42` becomes a logical update to
`int_store` in the WP calculus, not a change to a heap parameter.

### 2. The Frame Condition Is Declared, Not Threaded

Instead of returning a new heap, Frama-C uses **`\assigns` clauses** to declare which
memory regions a function may modify:

```c
/*@ requires \valid(list_a + (0..n-1));
  @ requires \valid(list_b + (0..n-1));
  @ requires \separated(list_a + (0..n-1), list_b + (0..n-1));
  @ assigns  list_a[0..n-1];
  @ ensures  list_a[0] == 42;
  @*/
void fill(int *list_a, int *list_b, int n);
```

The WP plugin automatically computes that `list_b` is unchanged from the `\assigns`
clause + `\separated` precondition. The heap is **never a function parameter** — it is
always implicit.

### 3. The Memory Model Is Parameterised

Frama-C WP offers four memory model backends:

| Model | Description | Aliasing |
|---|---|---|
| `Hoare` | No heap, all variables are value-typed | Not supported |
| `Typed` | One typed map per C type | Safe for non-aliasing |
| `Store` | Single untyped byte array | Full C aliasing |
| `Cast` | Like Store but with explicit type casts | Full with casting |

For most industrial use, `Typed` is the default — it closely matches Approach 3's
"one map per type" intuition but keeps the heap implicit.

### 4. Validity and Separation Are First-Class Predicates

```c
\valid(p)                       (* p points to allocated, in-bounds memory *)
\valid(p + (0..n-1))            (* p..p+n-1 are all valid *)
\separated(p+(0..n), q+(0..m))  (* regions [p, p+n] and [q, q+m] are disjoint *)
\old(expr)                      (* value of expr at function entry *)
\at(expr, L)                    (* value of expr at program point L *)
```

These predicates are part of ACSL (the annotation language) and are verified by the WP
calculus directly.

---

## Detailed Comparison: Approach 3 vs Frama-C

### Expressiveness

| Capability | Approach 3 (Heap Threading) | Frama-C (Implicit Heap) |
|---|---|---|
| Model aliasing correctly | ✅ Yes — `a = b` in same map | ✅ Yes — `\separated` / `Typed` model |
| Pointer arithmetic | ✅ `Loc + offset` | ✅ `p + i` natively |
| Non-aliasing assertion | ✅ `requires a <> b` | ✅ `requires \separated(...)` |
| Frame conditions | Manual — caller tracks heap changes | ✅ Automatic from `\assigns` |
| Pre-state values | ✅ `h.contents[a+i]` | ✅ `\old(p[i])` |
| Memory validity | Manual — `valid h a n` precondition | ✅ `\valid(p + (0..n-1))` built-in |
| Pointer equality | ✅ `a = b` | ✅ `p == q` in ACSL |
| Type safety | Partial — single-typed heap | ✅ Per-type stores |
| Untyped/union aliasing | ❌ Requires multiple heaps | ✅ `Store` / `Cast` models |

### Proof Obligation Shape

**Approach 3** generates proof goals like:

```
∀ h a b n.
  valid h a n →
  valid h b n →
  let h' = h[a+0 ← 42] in
  h'.contents[b+0] = (if a = b then 42 else h.contents[b+0])
```

The solver must reason about map updates explicitly. With Z3/Alt-Ergo this works well for
small fixed sizes; it scales poorly for large arrays with complex access patterns because
the solver must unfold the functional heap update chain.

**Frama-C WP** generates goals like:

```
\separated(list_a + (0..n-1), list_b + (0..n-1)) →
\old(list_b[0]) = list_b[0]
```

The `\assigns` clause + `\separated` directly give the solver a **locality lemma** it
can use without unfolding anything. This is substantially easier for SMT solvers.

### Annotation Burden on the Developer

**Approach 3:** Every function that touches memory must accept a `heap` parameter and
return one. Callers must thread the heap through call sequences:

```whyml
let h1 = fill  h0 a b n in
let h2 = sort  h1 a n   in
let h3 = merge h2 a b n in
...
```

This is natural in functional languages (Haskell's `State` monad, OCaml's explicit
threading) but deeply alien to Python's imperative style. An LLM annotator asked to
produce these annotations would need to reason about heap lineages — far beyond what
current models can reliably do.

**Frama-C:** The programmer writes `\assigns` clauses and `\valid`/`\separated`
preconditions. The heap threading is handled automatically by the WP calculus. The
annotation burden is comparable to PyCSL's current contract style.

### Integration with Why3

Approach 3 can be implemented in Why3 today using `map.Map` and a `ref` to the heap, or
purely functionally with a heap passed as a value. Why3's standard library provides:

```whyml
use map.Map     (* Loc → value maps *)
use map.MapEq   (* map equality over regions *)
use map.Const   (* constant maps *)
```

A complete heap model would add:

```whyml
type loc = int
type heap = { mutable store: map loc int }

predicate valid (h: heap) (l: loc) (n: int) =
  forall i. 0 <= i < n -> (* some allocation model *)

predicate separated (l1: loc) (n1: int) (l2: loc) (n2: int) =
  l1 + n1 <= l2 \/ l2 + n2 <= l1
```

This is implementable in Module 6 with a new `needs_heap` flag, similar to how
`needs_array` was added for Feature 1.

### The Key Architectural Difference

Frama-C separates concerns cleanly:

```
Annotation language (ACSL)  →  \valid, \separated, \assigns, \old
         ↓
WP calculus                 →  automatically threads the heap through the VCs
         ↓
Memory model backend        →  Typed / Store / Cast (chosen per proof goal)
         ↓
SMT solver                  →  sees locality lemmas, not raw map updates
```

Approach 3 collapses the WP calculus and memory model backend into the annotation
language itself — the programmer is doing by hand what Frama-C's WP engine does
automatically.

---

## Pros and Cons Summary

### Approach 3 — Explicit Heap Threading

**Pros:**
- Correct aliasing semantics with no special-purpose logic
- Implementable directly in Why3 with `map.Map`
- No new grammar primitives needed (heap is just another parameter)
- Natural fit for purely functional reasoning styles (Coq, Isabelle)
- Transparent: the proof state at every point is a heap value you can inspect
- The aliasing case (`a = b`) is handled automatically — no separate case split needed

**Cons:**
- Annotation burden is very high — every function signature changes
- LLMs cannot reliably generate heap-threaded contracts in Python style
- Proof obligations are large functional map-update chains (SMT-hard at scale)
- Alien to Python's imperative semantics
- Caller must manually compose heap transformations at every call site
- No built-in `\valid` / `\separated` predicates — must define from scratch
- Does not scale well to programs with many heap-touching call sites

### Frama-C Memory Model (as a target for PyCSL)

**Pros:**
- `\assigns` automatically generates the frame condition (no heap threading)
- `\valid` and `\separated` are built-in, well-understood predicates
- The WP calculus generates compact, solver-friendly proof obligations
- Scales to industrial C codebases
- Typed memory model handles arrays, struct fields, and pointer arithmetic uniformly
- Proven track record (DO-178C avionics, Common Criteria EAL6+ evaluations)
- The annotation style (`requires`, `ensures`, `assigns`) maps directly to PyCSL's
  existing grammar

**Cons:**
- Designed for C's low-level pointer model — Python has no `*p` syntax
- Requires `\valid` annotations on every pointer parameter (boilerplate)
- The `Typed` model is unsound for union aliasing (need `Store` model, harder proofs)
- Significant engineering effort to replicate `\assigns` frame-condition inference
  in a Python→WhyML pipeline
- `\separated` is a binary predicate — with N arrays you need O(N²) separation clauses

---

## Conclusion for PyCSL

Approach 3 is the right **long-term architectural direction** if PyCSL grows into a
full heap-aware verifier, but the annotation and proof cost make it impractical today.
The Frama-C model is superior in engineering terms — implicit heap + `\assigns` +
`\separated` produces compact, solver-friendly obligations — but replicating it requires
a significant investment in the contract grammar (Module 2), the semantic analyser
(Module 4), and the WhyML emitter (Module 6).

The pragmatic near-term path remains **Approach 1**: `#@ requires list_a != list_b` as
an explicit non-aliasing precondition. This is a one-line approximation of Frama-C's
`\separated(list_a + (0..n-1), list_b + (0..n-1))`. It rules aliasing out rather than
modelling it, but that is sufficient for the vast majority of algorithms PyCSL currently
targets.

If aliasing support were to be implemented, the recommended path would be to adopt the
**Frama-C model** (Approach 2.5): keep the heap implicit, add `\separated` and `\valid`
predicates to Module 2's grammar, and use `\assigns` clause inference in Module 5 to
automatically generate frame conditions — rather than threading the heap explicitly
through every function signature as Approach 3 requires.
