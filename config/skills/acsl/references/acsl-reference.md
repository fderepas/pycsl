# ACSL Reference (ANSI/ISO C Specification Language)

Exhaustive working reference for ACSL as implemented by Frama-C. ACSL is a
*behavioral interface specification language*: specifications are written as C
comments and are ignored by the C compiler but read by Frama-C.

## Table of contents
1. Annotation syntax
2. Function contracts
3. Behaviors and case analysis
4. Termination clauses
5. Statement annotations (assert / check / admit)
6. Loop annotations
7. Ghost code
8. The logic language (predicate, logic, lemma, axiomatic, inductive, type)
9. Built-in predicates and functions (memory model)
10. Labels, \at, \old, \result
11. Logic types, terms, sets and ranges
12. Data invariants and model variables
13. Toolchain (WP, Eva, E-ACSL, RTE, provers)
14. Common pitfalls

---

## 1. Annotation syntax

- Single line: `//@ <annotation>`
- Block: `/*@ <annotation> */`
- A **function contract** is placed immediately before the function definition or
  declaration.
- **Statement annotations** (`assert`, loop clauses, statement contracts) are
  placed before the relevant statement.
- **Global logic** (predicates, lemmas, axiomatics) lives at file scope.
- `//@ ghost <C declaration/statement>` introduces specification-only code.

---

## 2. Function contracts

A contract is a set of clauses. The default (unguarded) clauses form the
*global* / *default behavior*.

```c
/*@ requires valid_read: \valid_read(a + (0 .. n-1));
    requires positive_n: n > 0;
    assigns  \nothing;
    ensures  \result == a[0] || \exists integer i; 0 <= i < n && \result == a[i];
    ensures  \forall integer i; 0 <= i < n ==> a[i] <= \result;
*/
int array_max(const int* a, int n);
```

Core clauses:

- **`requires P;`** — precondition; obligation on the caller, hypothesis for the
  body.
- **`ensures Q;`** — postcondition; obligation on the body, hypothesis for the
  caller. May use `\result` and `\old(...)`.
- **`assigns loc1, loc2, ...;`** — *frame condition*: the only (non-local)
  locations the function may modify. `assigns \nothing;` means it is pure (no
  side effects on the state). **Omitting `assigns` defaults to "may modify
  anything", which destroys modular proofs of callers** — always write it.
- **`assigns loc \from deps;`** — additionally declares that the new value of
  `loc` depends only on `deps` (functional dependency / data-flow). Useful for
  Eva and for relational reasoning.
- **`allocates p;` / `frees p;`** — dynamic-memory frame: which locations become
  newly allocated / freed. Pair with `\fresh`, `\freeable`.

Clause labels (the `valid_read:` / `positive_n:` prefixes above) are optional
names that make proof results and failures readable — use them.

---

## 3. Behaviors and case analysis

A `behavior` is a named guarded sub-contract. Use it to specify distinct cases.

```c
/*@ requires \valid(p);
    assigns  *p;

    behavior positive:
      assumes  *p > 0;
      ensures  *p == \old(*p);          // unchanged

    behavior nonpositive:
      assumes  *p <= 0;
      ensures  *p == 0;                 // clamped

    complete behaviors;                 // the assumes cover all cases
    disjoint behaviors;                 // the assumes never overlap
*/
void clamp(int* p);
```

- **`assumes C;`** — guard selecting when the behavior applies (only meaningful
  inside a `behavior`).
- **`requires` / `ensures` / `assigns` / `allocates` / `frees`** inside a
  behavior are conditional on its `assumes`.
- **`complete behaviors;`** — asserts the guards cover every case reachable under
  the precondition.
- **`disjoint behaviors;`** — asserts at most one guard holds at a time.
- `complete`/`disjoint` may list specific behavior names:
  `complete behaviors positive, nonpositive;`.

---

## 4. Termination clauses

- **`terminates P;`** — under condition `P`, the function is guaranteed to
  terminate. (`terminates \true;` for always-terminating.)
- **`decreases m;`** or **`decreases m for R;`** — for **recursive functions**, a
  measure `m` (an `integer`, or a term under a well-founded relation `R`) that
  strictly decreases on each recursive call, proving the recursion bottoms out.
  (Loops use `loop variant`, see §6.)

Abrupt-termination clauses constrain non-normal exits:

- **`exits P;`** — what holds when the function leaves via `exit()`.
- **`returns P;`** — postcondition specifically for `return` (vs. abrupt).
- **`breaks P;` / `continues P;`** — for statement contracts around loops.

---

## 5. Statement annotations

Placed before a statement:

- **`//@ assert P;`** — `P` must hold here; afterward `P` is *assumed* as a
  hypothesis for the rest of the proof.
- **`//@ check P;`** — `P` is verified here but **not** added as a hypothesis
  afterward (a pure sanity check that cannot accidentally strengthen later
  reasoning).
- **`//@ admit P;`** — `P` is assumed **without** being proved (an explicit,
  auditable hole; use sparingly).
- These modifiers also prefix contract clauses: `check requires`, `admit ensures`,
  etc., letting you mark individual clauses as check-only or assumed.
- **Statement contracts**: a full `requires/ensures/assigns` block can wrap an
  arbitrary statement or block, not just a function.

---

## 6. Loop annotations

Every loop should carry three kinds of clause:

```c
/*@ loop invariant 0 <= i <= n;
    loop invariant \forall integer k; 0 <= k < i ==> a[k] == 0;
    loop assigns i, a[0 .. n-1];
    loop variant n - i;
*/
for (int i = 0; i < n; i++) a[i] = 0;
```

- **`loop invariant I;`** — must hold on loop entry **and** be preserved by every
  iteration (it must be *inductive*). The conjunction of invariants, together
  with the negated loop condition, must imply what follows the loop. This is
  where most manual effort goes.
- **`loop assigns locs;`** — frame condition for the whole loop; what the body
  may modify. Required for sound reasoning across iterations.
- **`loop variant V;`** — a term that is `>= 0` and **strictly decreases** each
  iteration, proving termination. For a well-founded relation other than `<` on
  integers: `loop variant V for R;`.
- Loop behaviors (`for name: loop invariant ...`) attach invariants to named
  behaviors of an enclosing contract.

---

## 7. Ghost code

Specification-only code that exists for the proof and never affects the C
semantics:

```c
//@ ghost int seen = 0;
//@ ghost seen += 1;

/*@ requires \valid(a + (0..n-1));
    assigns  \nothing;
*/
void f(int* a, int n) {
  //@ ghost int witness;
  /* ... use witness in assertions to guide the prover ... */
}
```

- Ghost variables, ghost statements, ghost function parameters (`/*@ ghost ... */`
  in the parameter list).
- **Lemma functions**: ordinary-looking (ghost) C functions whose contract states
  a lemma and whose body *constructs the proof* step by step (e.g. building a
  witness, doing an induction by recursion). A widely used auto-active technique
  to avoid interactive proof — see the bibliography (Volkov et al., Linux kernel
  string functions).
- Ghost code must not write to non-ghost locations; Frama-C enforces this
  separation so ghosts cannot change observable behavior.

---

## 8. The logic language

Define reusable specification vocabulary at global scope.

**Predicate** (a named boolean proposition):
```c
/*@ predicate sorted(int* a, integer n) =
      \forall integer i, j; 0 <= i <= j < n ==> a[i] <= a[j];
*/
```

**Logic function** (a named term, any logic type):
```c
//@ logic integer sum(int* a, integer lo, integer hi) = /* ... */;
```

**Lemma** (a proposition to prove once and reuse as a hypothesis):
```c
//@ lemma sorted_sub: \forall int* a, integer n; sorted(a, n) ==> sorted(a, n-1);
```
Lemmas are discharged by WP like any goal; hard ones may need Coq/Why3.

**Axiomatic block** (group of logic symbols plus `axiom`s — the usual way to
define *recursive* logic functions/predicates that can't be written as a direct
equation):
```c
/*@ axiomatic Count {
      logic integer count(int* a, integer lo, integer hi)
        reads a[lo .. hi-1];
      axiom count_empty:
        \forall int* a, integer lo; count(a, lo, lo) == 0;
      axiom count_rec:
        \forall int* a, integer lo, hi; lo < hi ==>
          count(a, lo, hi) == count(a, lo, hi-1) + (a[hi-1] != 0 ? 1 : 0);
    }
*/
```
> Caution: inconsistent axioms silently make *everything* provable. Prefer
> `inductive`/direct definitions where possible, and add `check \false;` smoke
> tests.

**Inductive predicate** (least fixpoint defined by cases):
```c
/*@ inductive reachable(node* root, node* n) {
      case here:  \forall node* r; reachable(r, r);
      case step:  \forall node* r, *n; reachable(r, r->next) ==> reachable(r, n);
    }
*/
```

**Logic type definitions** (`//@ type point = ...;`) and `\let x = e; P` for
local bindings inside a formula.

---

## 9. Built-in predicates and functions (memory model)

Validity and separation:
- **`\valid(p)`** — `p` points to a currently allocated, writable location.
  Ranges: **`\valid(p + (0 .. n-1))`**.
- **`\valid_read(p)`** — readable (weaker than `\valid`); use for `const` data.
- **`\separated(p, q)`** — the locations/ranges do not overlap (anti-aliasing).
  Variadic: `\separated(a+(0..n-1), b+(0..m-1))`.
- **`\initialized(p)`** — the location has been written (no indeterminate read).
- **`\dangling(p)`** — points to an out-of-scope/freed object.

Allocation:
- **`\fresh{L1,L2}(p, n)`** — `p` is newly allocated (not valid at `L1`, valid for
  `n` bytes at `L2`); used in postconditions of allocators.
- **`\allocable(p)` / `\freeable(p)`** — `p` can be allocated / safely `free`d.

Memory geometry:
- **`\block_length(p)`** — size in bytes of the allocated block containing `p`.
- **`\base_addr(p)`** — start address of that block.
- **`\offset(p)`** — byte offset of `p` within its block.
- **`\null`** — the null pointer.

---

## 10. Labels, \at, \old, \result

ACSL terms are evaluated at a **program point** named by a *label*.

- Built-in labels: **`Pre`** (function entry), **`Post`** (exit), **`Here`**
  (current point), **`Old`** (= `Pre` in postconditions), **`LoopEntry`** /
  **`LoopCurrent`** (loop), **`Init`** (after global initialization).
- **`\at(e, L)`** — value of `e` evaluated at label `L`.
- **`\old(e)`** — shorthand for `\at(e, Pre)`, valid in postconditions.
- **`\result`** — the function's returned value, valid in `ensures`/`returns`.
- C labels can be referenced: write `L:` in code, then `\at(x, L)` in a spec.

Example: `ensures *p == \old(*p) + 1;` and
`loop invariant \at(sum, LoopEntry) <= sum;`.

---

## 11. Logic types, terms, sets and ranges

- **`integer`** — unbounded mathematical integers (no overflow). **`real`** —
  mathematical reals. **`boolean`** — logic booleans (`\true`/`\false`).
- C integer/float types coerce into `integer`/`real`; the *reverse* needs an
  explicit cast and may add proof obligations.
- **Quantifiers**: `\forall integer i; P` and `\exists integer i; P`. Bound
  ranges by hand: `\forall integer i; 0 <= i < n ==> ...`.
- **Connectives**: `==>` (implies), `<==>` (iff), `&&`, `||`, `!`, `^^` (xor).
- **Ranges and sets**: `a[lo .. hi]` is a *set* of locations; `(lo .. hi)` is an
  integer range; set comprehension `{ f(x) | integer x; P(x) }`. Sets are used
  in `assigns`, `\valid`, `\separated`, etc.
- **`\let`** bindings, conditional terms `c ? e1 : e2`, and casts `(integer)x`.

---

## 12. Data invariants and model variables

- **`//@ type invariant Inv(struct S s) = ...;`** — an invariant attached to a
  type, expected to hold for all values of that type at relevant points.
- **`//@ global invariant g_inv: ...;`** — a property of globals. ACSL
  distinguishes *strong* invariants (hold at every point) from *weak* invariants
  (hold at function boundaries) — note this is exactly the distinction MetAcsl
  generalizes with its `strong_invariant`/`weak_invariant` contexts.
- **Model fields/variables** (`//@ model ...;`) add logic-only state to a type for
  abstraction. Tool support varies; use when you need to hide a representation.

---

## 13. Toolchain

Frama-C is a plug-in platform; ACSL is the shared specification language.

- **WP** — weakest-precondition deductive verification. Compiles contracts into
  proof obligations, dispatched through **Why3** to SMT solvers (**Alt-Ergo,
  Z3, CVC5**) and, for hard goals, interactive provers (**Coq**). Has several
  memory models (typed, Hoare, bytes) trading precision for automation.
- **Eva** — abstract interpretation; computes a sound over-approximation of all
  reachable states. Best for proving *absence of runtime errors* and value
  ranges across whole programs; can validate many ACSL assertions automatically.
- **E-ACSL** — translates a large executable subset of ACSL into C instrumentation
  that checks annotations **at runtime** and aborts on violation. Bridges formal
  specs and testing.
- **RTE** — generates ACSL assertions for potential runtime errors (overflow,
  invalid memory access, division by zero, ...). Run it (or `-wp-rte`) so proofs
  account for undefined behavior. **Functional proofs without RTE are usually
  unsound in practice.**

Typical invocations:
```
frama-c file.c -wp -wp-rte                      # deductive proof + RTE guards
frama-c file.c -eva                             # value/abstract-interpretation analysis
frama-c file.c -e-acsl -then-last -print        # runtime-checking instrumentation
frama-c-gui file.c -wp -wp-rte                  # interactive: inspect goals
```

---

## 14. Common pitfalls

- **No `assigns`** → caller proofs collapse (callee "may modify everything").
- **Non-inductive loop invariant** → holds on entry, not preserved; WP fails at
  the preservation goal, not the establishment goal.
- **`integer` vs `int`** → spec is overflow-free but RTE demands no machine
  overflow; constrain inputs with `requires`.
- **Aliasing** → forgotten `\separated`; two pointer params silently allowed to
  overlap.
- **Inconsistent `axiomatic`** → everything "proves"; add `check \false;` smoke
  tests and prefer `inductive`/direct definitions.
- **Reading `\old` outside a postcondition**, or `\result` in a `requires` →
  ill-formed; labels matter.
