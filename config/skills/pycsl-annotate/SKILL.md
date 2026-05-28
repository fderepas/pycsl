---
name: pycsl-annotate
description: Annotates Python code with PyCSL Hoare-logic contracts (requires, ensures, assigns, loop invariants, loop variants) that compile to WhyML and are discharged by SMT solvers like Z3 and Alt-Ergo. Covers PyCSL syntax, memory-model extensions, quantifiers, class invariants, transpiler-specific limits, and solver-friendly invariant patterns. Use this skill whenever the user asks to annotate Python with formal contracts, add invariants to loops, verify PyCSL-annotated Python code with Why3 or an SMT solver, work with PyCSL, or convert imperative code into a verifiable specification — even when they describe the task informally as "add contracts," "make this provable," or "prove this function correct."
---

# PyCSL Annotator

You are a formal verification engineer. Your task is to analyze Python code and inject Design-by-Contract annotations using PyCSL — a custom contract language that compiles to WhyML and is verified by SMT solvers (Alt-Ergo, Z3).

## Workflow

**Before writing any contract, read the entire function and understand its purpose.** Ask: *What is this function computing? What mathematical or logical property does it guarantee?* Then express that as the postcondition. A postcondition must capture the function's intended behaviour — not just be a placeholder. For example:

- A function that finds the maximum should have `#@ ensures \result >= 0` (or a tighter bound if provable).
- A function that counts elements satisfying a property should have `#@ ensures \result >= 0` and `#@ ensures \result <= n`.
- A function that computes a sum of non-negative inputs should have `#@ ensures \result >= 0`.
- A method that deposits money should have `#@ ensures self._balance == \old(self._balance) + amount`.
- A function that returns `len(collection)` (or `length` of an array parameter) should have `#@ ensures \result >= 0` — Python's `len()` always returns a non-negative integer but **can return 0** for an empty collection. Only strengthen to `#@ ensures \result >= 1` if there is an explicit precondition that constrains the collection to be non-empty (e.g., `#@ requires \length(arr) >= 1`).

Reserve `#@ ensures True` only when no useful property of the return value is provable given the constraints of the grammar (e.g., a sum over an arbitrary signed list). `True` is the recommended form for vacuous postconditions; the older `1 == 1` idiom is still accepted but discouraged.

## Required on every function

Every function definition MUST have **all three** of `#@ requires`, `#@ ensures`, and `#@ assigns` — placed immediately before the `def` keyword, with **no blank lines** between the last `#@` line and the `def`. The pipeline uses line numbers from libcst's `PositionProvider` to match contracts to AST nodes; a blank line causes a line-number mismatch that silently drops all contracts for that function or class.

Every **recursive** function (a function that calls itself by name) MUST additionally include `#@ \variant <param>` — placed immediately before the `def` line, after `#@ assigns`, so PyCSL emits `let rec` with `variant { param }` in WhyML and the termination sub-goal can be discharged. Without this clause Why3 will time out on the termination obligation. The variant expression must be the parameter that decreases toward the base case (e.g., `n` for `factorial(n)`).

Every `while` and `for` loop MUST have `#@ loop invariant` and `#@ loop variant` — placed immediately before the loop keyword.

Add PEP 484 type hints to **all** function parameters and return types, even if missing in the input. Scripts with no annotations at all must be fully annotated from scratch.

---

## Section 1 — Function and loop contracts

**Function contracts** are placed immediately before the `def` keyword:

- `#@ requires <expr>` — Preconditions that must hold before execution.
- `#@ ensures <expr>` — Postconditions guaranteed after execution. Use `\result` for the return value.
- `#@ assigns <var1, var2> | \nothing` — Frame condition: what global state or references are modified.
- `#@ \variant <expr>` — Termination measure for recursive functions (must decrease, stay ≥ 0). Emits `let rec` + `variant { expr }` in WhyML.
- `#@ \variant (<expr>, <ordering>)` — Structural variant via a named well-founded ordering. Emits `variant { expr } with ordering`.
- `#@ \diverges` — Declares the function may not terminate (no termination proof required). Cannot be combined with `\variant`.
- `#@ \trusted` or `#@ \trusted reviewer: <name>` — Body is not verified; contracts are assumed as axioms. Emits `val` (spec-only) instead of `let` + body. Callers may use the postcondition, but the implementation is not checked. The optional `reviewer:` clause names a human or process accountable for the trust assumption (e.g., `reviewer: alice` or `reviewer: pycsl-self-annotate`); it is captured by Module 3 / Module 5 but does not affect WhyML emission. Anonymous `\trusted` (no `reviewer:`) produces a warning; the convention is to always include one. See `annotations.md` §2.1.7 for the reviewer-tag convention.
- `#@ assumes bounded_int(N)` — Bounded integer pragma (N = 32 or 64). All `int` params/locals become `intN` machine integers; arithmetic (`+`, `-`, `*`) auto-generates overflow proof obligations.
- `#@ raises ExcType when <cond>` — Exceptional postcondition. Declares that the function may raise `ExcType` when `cond` holds. Emits `raises { ExcType -> cond }` in WhyML.
- `#@ no_exception E1, E2, ...` or `#@ no_exception \all` — Turns **implicit** Python exceptions into proof obligations. For each IR operation in the body that could raise a listed exception, Module 6 emits a WhyML `assert { trigger }` immediately before the operation; trigger conditions are looked up in `src/pycsl/exception_model.py`. Phase 1 exceptions: `ZeroDivisionError`, `IndexError`, `KeyError`, `ValueError`, `StopIteration`. Cannot be combined with `raises { E -> _ }` for the same `E`. The `\all` form additionally requires the `raises { }` set to be empty.
- `#@ allow_finalizer` — Class-level escape annotation. Place immediately before the `class` keyword to opt a class with a `__del__` method out of UB-7.5's hard rejection. Use *only* when the class genuinely needs a finalizer (rare in verification-grade code); the annotation documents the boundary but does not make the finalizer verifiable.
- `#@ allow_iteration_mutation` — Loop-level escape annotation. Place immediately before a `for` statement to opt out of UB-7.1's mutation-during-iteration check. Use *only* when the loop intentionally mutates the iterated container (the `for k in list(d):` snapshot pattern is the canonical case).
- `#@ proof <rocq|lean> <qualname>` — **Axiom import** (`test-suite/annotations.md` §2.1.12). Imports a Rocq or Lean theorem as a Why3 axiom in the WhyML preamble. **Module-level** (placed before any function definition). The directive has real semantic effect — Alt-Ergo/Z3 may use the imported axiom to discharge obligations. **The annotator agent MUST NOT generate `#@ proof` lines** unless `proof2why3` has been run and the cross-check manifest shows `reconciled` status for the target. **Namespace-aware audit:** the cited `<qualname>` is enforced as a real namespace path — for `Pycsl.Reference.Gcd.gcd_step`, the theorem must live inside `Module Pycsl. Module Reference. Module Gcd.` (Rocq) or `namespace Pycsl.Reference.Gcd` (Lean) in `<file>.proofs/{rocq,lean}/<file>.{v,lean}`. Run `pycsl --audit-proof <file>` to verify. **Worked example: `test-suite/corpus/pycsl-reference/0342.py`** (Euclidean GCD, with proofs under `0342.proofs/{rocq,lean}/`).
- `#@ ghost <name> = <expr>` — Ghost variable declaration/assignment. Place before any statement. First occurrence → `let ghost <name> = ref <val> in`; subsequent → `ghost <name> := <val>`.
- `#@ ghost <name> : <type> = <expr>` — Typed ghost variable declaration. `<type>` is one of: `int` (default), `string`, `array`, `ghost_dict`, `ghost_list`, `ghost_set`, `tuple2`, `tuple3`, `tuple4`.
- `#@ ghost <name> += <expr>` — Ghost augmented assignment (`+=`, `-=`, `*=`). Ghost variables are erased at extraction but usable in contracts and loop invariants.
- `#@ ghost <arr>[i] = <expr>` — Ghost array element assignment (in-place mutation, for `array`-typed ghosts only).

**Loop contracts** are placed immediately before the `while` or `for` keyword:

- `#@ loop invariant <expr>` — Property that holds before and after every iteration.
- `#@ loop variant <expr>` — A strictly decreasing non-negative integer expression that proves termination.

`for` loops with `continue` and early `return` are supported — annotate them just like `while` loops.

---

## Section 2 — Operators and quantifiers

**Comparison and arithmetic:** `==`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `/`, `//`

**Boolean:** `and`, `or`, `not`

**Implication:** `==>` (implies), `<==>` (iff)

**Pre-state values:** `\old(var_name)` — refers to the value at function entry.

**Quantifiers:** Write `\forall i; body` and `\exists i; body` (the alias `\exist` without trailing `s` is accepted). The bound variable `i` ranges over integers; write the range as part of the body using `==>`:

```python
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= 0
```

Quantifiers may appear at the top level of an expression **or** as the right-hand side of `==>`, `and`, and `or` without parentheses:

```python
#@ loop invariant found == 0 ==> \exists j; i <= j and j < n and arr[j] == target
```

---

## Section 3 — Memory model extensions

The memory model is selected globally and affects all functions in a file. Default is `"hoare"`. Set in `config/agents-config.json` (`"memory-model": "hoare" | "typed" | "store"`) or override with `pycsl --memory-model typed input.py`.

**Choosing a model:**

- **`hoare`** (default): pure value semantics, arrays are `array int`, no aliasing. Best for most algorithms where parameters don't alias.
- **`typed`**: required when you need pointer-aliasing reasoning, heap validity, frame conditions, or any of `\valid` / `\separated` / `\assigns arr[lo..hi]` / `\at` with array subscripts.
- **`store`**: identical to `typed` but uses a different internal heap variable name. No annotation difference from the annotator's perspective.

**`\assigns arr[lo..hi]`** (Phase 0) — Declares the function may modify `arr[lo]` through `arr[hi-1]` (`..` is a half-open range). In hoare model: recorded but no frame emitted (no heap). In typed/store: emits `writes { int_mem }` plus a quantified `ensures` preserving elements outside `[lo..hi]`.

**`\valid(arr, n)`** (Phase 1) — Asserts `arr` is a valid array of length ≥ `n`. In hoare: `n >= 0 && n <= length arr`. In typed/store: `(valid !int_mem arr n)`.

**`\separated(a, na, b, nb)`** (Phase 1) — Asserts regions `a[0..na-1]` and `b[0..nb-1]` do not overlap. In hoare: trivially `true` (no aliasing). In typed/store: `(separated a na b nb)`.

**`\old(arr[i])`** (Phase 3) — Value of `arr[i]` at function entry. In hoare: `(old arr[i])`. In typed/store: `Map.get (old !int_mem) (arr + i)`.

**`#@ label L`** (Phase 5) — Marks a program point. Place immediately before any Python statement (no blank lines). The label scope extends to the end of the function. Reference with `\at(expr, L)`:

```python
#@ label PRE
... code ...
#@ ensures arr[i] == \at(arr[i], PRE)
```

In hoare: `(expr at L)`. In typed/store: `Map.get (int_mem at L) (arr + i)` for array elements.

**`#@ ghost <name> = <expr>`** (Phase 5) — Ghost variable for verification only. Place before any statement, including inside loop bodies. First occurrence declares; subsequent update. Use in invariants to track iteration counts, sums, or history.

```python
#@ ghost count = 0
#@ loop invariant count == i
while i < n:
    #@ ghost count += 1
    i = i + 1
```

Ghost variables emit `let ghost <name> = ref <val> in` (declaration) or `ghost <name> := <val>` (update) in WhyML. They are erased during Why3 extraction.

**Pattern: snapshot parameter entry values when the body mutates parameters.** When a function reassigns its own parameters (e.g., `a, b = b, a % b` in a Euclidean loop), `\old(a)` inside the loop invariant emits `old !a` (an `old` over a shadowed-ref deref) which Alt-Ergo can struggle to discharge. Capture the entry values as ghost variables at function entry and use those names instead. The ensures clause can still reference `a, b` directly — at the contract scope, parameters refer to their entry values regardless of body mutation:

```python
def gcd(a: int, b: int) -> int:
    #@ ghost a0 = a
    #@ ghost b0 = b
    #@ loop invariant gcd(a, b) == gcd(a0, b0)
    #@ loop variant b
    while b != 0:
        a, b = b, a % b
    return a
```

Worked example: `test-suite/corpus/pycsl-reference/0352.py` (compare with 0342.py which uses sequential local vars and doesn't need the snapshot). See `references/transpiler-limits.md` §4 for the full discussion.

**Terminology note:** `#@ ghost ...` statements are **ghost code**; the
verification-only values they maintain form **ghost state**; their translation
through the IR and WhyML pipeline is **ghost lowering**. When several ghost
encodings are possible, prefer witness carriers that support **local reasoning**
(explicit array/dict/tuple lookups) over **global reasoning** that spends solver
budget on wide quantifiers or list membership.

**Typed ghost variables** use a type annotation: `#@ ghost s : string = "hello"`. Available types:

| Type | WhyML type | Initial value | Usage |
|---|---|---|---|
| `int` (default) | `ref int` | any int expr | `ghost x += 1` |
| `string` | `ref string` | `"literal"` | `ghost s = s ^ "chunk"` |
| `array` | `array int` | `\copy(arr)` or `\make(n, v)` | `ghost snap[i] = e` |
| `ghost_dict` | `ref (map int (option int))` | `\empty_map` | `ghost d = \map_set(d, k, v)` |
| `ghost_list` | `ref (list int)` | `\nil` | `ghost l = \cons(x, l)` |
| `ghost_set` | `ref (map int bool)` | `\set_empty` | `ghost s = \set_add(s, x)` |
| `tuple2` | `ref (int, int)` | `\mktuple(a, b)` | `ghost p = \mktuple(a, b)` |
| `tuple3` | `ref (int, int, int)` | `\mktuple(a, b, c)` | `ghost t = \mktuple(a, b, c)` |
| `tuple4` | `ref (int, int, int, int)` | `\mktuple(a, b, c, d)` | `ghost q = \mktuple(a, b, c, d)` |

Ghost expression atoms for typed ghosts (use in contracts and loop invariants):
- **Tuples:** `\mktuple(e1, e2, ...)`, `\fst(t)`, `\snd(t)`, `\proj(t, i)` (i must be an integer literal)
- **Strings:** `s ^ t` (concatenation), `"literal"`, `\str_length(s)`, `\str_sub(s, lo, hi)`
- **Ghost arrays:** `\copy(arr)`, `\copy_range(arr, lo, hi)` (bounded snapshot → `Array.sub arr lo (hi-lo)`), `\make(n, v)` (hoare model only); `snap[i]` for element read in contracts/invariants; `#@ ghost snap[i] = expr` for element write. Provide bounds (`lo >= 0`, `lo <= hi`, `hi <= \length(arr)`) as preconditions or loop invariants before the declaration point.
- **Ghost dicts:** `\empty_map`, `\map_get(d, k)` (returns 0 if absent), `\map_set(d, k, v)`, `\map_eq(d1, d2)`, `\has_key(d, k)` (true iff key is present, option-type: safe even when 0 is a valid stored value), `\map_remove(d, k)` (removes key k); shorthand: `#@ ghost d += \mktuple(k, v)` for map-set
- **Ghost lists:** `\nil`, `\cons(x, l)`, `\hd(l)`, `\tl(l)`, `\list_length(l)`, `\nth(l, i)`, `\mem(x, l)`, `\append(l1, l2)`; shorthand: `#@ ghost l += x` for prepend. **CRITICAL**: use `\nth(log, 0)` for head tracking in provable invariants — `\mem` causes prover OOM; `\hd` is invalid in spec context.
- **Ghost sets:** `\set_empty`, `\set_add(s, x)`, `\set_remove(s, x)`, `\set_mem(x, s)`, `\set_card(s, lo, hi)`, `\set_union(s1, s2)`, `\set_inter(s1, s2)`, `\set_diff(s1, s2)`, `\set_subset(s1, s2)`, `\set_eq(s1, s2)`; shorthand: `#@ ghost s += x` for add

---

## Section 4 — Forbidden in contract expressions

**Three-level validation**: every `#@` expression must clear syntax (Level 1), static-semantics (Level 2), and WhyML-generation (Level 3) checks. `pycsl --no-proof` succeeding only guarantees Levels 1 and 2; Level 3 is verified by Why3. The most dangerous trap: contracts that pass Module4 yet fail Why3 (e.g., `"key" in d` when `d` is unannotated → `int` in WhyML, `in` on `int` is invalid). See `references/validation-stack.md` for the IS/SR/TR rule tables and the practical decision checklist.

> **Full list:** See `references/forbidden-expressions.md` for the complete set of NEVER rules (50+ entries).

Key rules (most common mistakes):

- **NEVER use arbitrary function calls** (e.g., `abs(x)`, `range(x)`, `len(x)`) inside `#@` expressions. Use `\length(arr)` instead for array lengths.
- **`True`, `False`, `None` ARE supported** as first-class contract atoms (annotations.md §3.1.18, §3.1.19). Prefer `True` over `1 == 1` for vacuous preconditions, and `False` over `0 == 1` for intentionally-unprovable postconditions. `None` maps to `0` in WhyML.
- **`//` and `%` ARE allowed** in contracts — they map to WhyML `div` and `mod` (confirmed by test 0334). Earlier notes were wrong about them being forbidden.
- **NEVER use `**`** (exponentiation) in contracts — use literal constants instead.
- **NEVER place blank lines** between a `#@` block and the `def`/`class` it annotates.
- **NEVER name variables `val` or `match`** — reserved WhyML keywords.
- **NEVER use `return <value>` inside `if` in a `while` loop** — use flag+sentinel pattern (see Example 6).
- **NEVER use `==>` in `ensures`** for index-loop functions — always times out.
- **NEVER emit duplicate contract clauses** for the same function.
- **`\old(arr)` is NOT supported** — only `\old(scalar)` and `\old(arr[i])` work. If you need to compare the whole array's entry value to its exit value, use a ghost snapshot via `\copy(arr)` or `\copy_range(arr, lo, hi)` immediately on entry, and reference `snap[i]` in the postcondition. The parser will reject `\old(arr)` with "Unexpected token `\\old`" near the `(`.

---

## Section 5 — Class support

> **Full details:** See `references/class-support.md` for complete method rules, `\old` usage, class invariants, and multi-class examples.

Key rules:

- Do NOT annotate `__init__` or `@property` — copy `__init__` verbatim.
- Use `self.field` in contracts; `\old(self.field)` in `ensures`.
- Each method needs all three contracts (`requires`, `ensures`, `assigns`).
- `#@ class invariant <expr>` goes immediately before `class` keyword.
- Method preconditions must be strong enough to maintain class invariants.

---

## Section 6 — Concurrent model (mutex-discipline verification)

Use `--memory-model concurrent` (or `pycsl-flags: --memory-model concurrent`) for files that use Python's `threading` module. This model reduces concurrency to sequential WP proofs using the monitor-invariant pattern.

**Module-level declarations** (place at the top of the file, before any `import` or `def`):

```python
#@ shared <var> protected_by <mutex>   # var is protected by the named mutex
#@ shared <var>                        # var is shared but unprotected (warning)
#@ mutex_invariant <mutex>: <expr>     # invariant that must hold while mutex is free
#@ lock_order <mutex1>, <mutex2>, ...  # total order for nested locking (deadlock prevention)
```

**Function-level annotations:**

```python
#@ thread_entry      # marks the function as a thread entry point
#@ acquires <mutex>  # function acquires mutex (for with-lock-as patterns)
#@ releases <mutex>  # function releases mutex
```

**Statement-level annotations** (place immediately before a `with` statement):

```python
#@ critical <mutex>  # declare this with-block is a critical section for <mutex>
```

**How verification works:**

1. At critical section entry: the verifier havoces all shared variables protected by `<mutex>` and `assume { mutex_inv }`.
2. Inside the section: verify the body sequentially.
3. At critical section exit: `assert { mutex_inv }` (must still hold after modification).

**Rules:**
- Shared variable writes MUST be inside a `#@ critical` (or `#@ acquires`/`#@ releases`) block — otherwise Module4 raises a semantic error.
- Nested locking REQUIRES `#@ lock_order` at module level.
- `queue.Queue`, `threading.Lock`, `threading.RLock` etc. are trusted thread-safe and need no `#@ shared` annotation.

**Minimal example:**

```python
#@ shared counter protected_by lock_counter
#@ mutex_invariant lock_counter: counter >= 0
import threading
lock_counter = threading.Lock()
counter = 0

#@ thread_entry
#@ \diverges
def worker() -> int:
    #@ critical lock_counter
    with lock_counter:
        counter += 1
    return 0
```

---

## Section 7 — Undefined-behaviour patterns (hard-reject)

> **Rulebook:** `config/skills/pycsl-ub-catalog/SKILL.md` is the
> normative reference for the five UB categories — detection
> mechanism, verification stance, error messages, corpus tests.
> Consult it before adding any escape annotation. This section is the
> annotator-workflow summary only.

Five Python patterns are hard-rejected before the proof obligation
is even generated. Authoring annotated code that trips one of these
checks produces a `PyCSLSemanticError`, not a proof failure — the
diagnosis points to a *structural* problem to rewrite or explicitly
bless.

| UB | Trigger | Escape annotation |
|---|---|---|
| 7.1 | Mutation of the iterated container inside `for x in C:` | `#@ allow_iteration_mutation` (per loop) |
| 7.2 | Class with both `__hash__` and `__eq__` | none — axiom mode by default; strict mode requires `#@ proof <prover>` |
| 7.3 | Shared-variable access outside `#@ critical` (concurrent model) | none — strict mode is opt-in (`--strict-concurrent-checks`) |
| 7.4 | `import ctypes` / `cffi` / `numpy.ctypeslib` / `cython` | `#@ \trusted` on at least one function in the file |
| 7.5 | Class with `__del__` | `#@ allow_finalizer` (per class) |

**Default for the annotator:** rewrite, don't bless. The reject
exists because the construct cannot be soundly modelled — the
escape annotation documents the assumption but does not make the
proof more meaningful. Reach for the catalog rulebook when you need
to decide between rewrite and bless.

---

## Section 8 — `no_exception` annotation patterns

> **Rulebook:** `config/skills/pycsl-exception-model/SKILL.md` is the
> normative reference for the trigger table, WhyML predicate
> vocabulary, inter-procedural propagation rules, and rules for
> extending the model. This section is the annotator-workflow
> summary only.

The `no_exception` directive turns implicit Python exceptions into
proof obligations (see Section 1 for syntax and forbidden
combinations). The annotator's job is to write a precondition strong
enough to discharge each operation's trigger:

```python
#@ requires n != 0
#@ ensures \result == 256 / n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def divide_256(n: int) -> int:
    return 256 // n
```

Two patterns the corpus has validated:

- **Direct precondition** — `requires n != 0` discharges
  `no_div_zero (n)` for `256 // n`. The whole value of `no_exception`
  is that a failed VC tells the caller exactly which precondition
  would discharge it.
- **Branching precondition (SMT-friendly)** — `requires n > 0 or n < 0`
  also discharges the zero-divisor obligation; Alt-Ergo splits and
  proves both branches.

**Inter-procedural call sites.** When a callee declares
`raises { E -> P }` and the caller declares `no_exception E`,
Module 6 wraps the call automatically (rulebook details in the
exception-model skill). The annotator's only responsibilities:

- Provide a caller precondition strong enough that `not P` holds at
  the call site.
- Avoid TR-BUG-2 in the callee — a `raises` callee with no
  local-variable mutation is emitted as `let function` (pure) which
  Why3 rejects as effectful. Add at least one local assignment in
  the callee body. (See "Transpiler workarounds" below for the
  worked example.)

---

## Section 9 — Stdlib stub awareness

> **Rulebook:** `config/skills/pycsl-stdlib-coverage/SKILL.md` is the
> normative reference for the three-artefact discipline
> (`calls-english.md`, `calls-pycsl.md`, `src/pycsl_lib/`), the
> discovery tool, the check loop, and the CPython version-bump
> workflow. This section is the annotator-workflow summary only.

Calls to standard-library APIs resolve through PyCSL's import
resolver to **curated stubs** under `src/pycsl_lib/` — each stub
declares `#@ \trusted` and provides the contract PyCSL trusts
without verifying the body. Practical implications for annotating a
function that calls stdlib:

- **Stub returns are `int`-valued in the model.** `os.path.exists(p)`
  returns 0 or 1; `re.compile(p)` returns an opaque non-negative
  integer; `len(x)` returns array length or `iter_length`.
- **The stub's postcondition propagates automatically** — claim
  `#@ ensures \result >= 0` after `return json.dumps(obj)` because
  the stub's postcondition already guarantees it. Don't re-prove
  what the stub already states.
- **Bare imports are fine.** `import os.path` resolves against the
  stub set; the pipeline never executes or fully parses CPython.

When a function uses an API with no existing stub, the annotator
has two options:

1. Add `#@ \trusted` to the using function (defer the obligation).
   Right for one-off utility callers.
2. Add the entry to the three-artefact set
   (`calls-english.md` + `calls-pycsl.md` + a stub under
   `src/pycsl_lib/`). Required when the call appears frequently or
   when the surrounding module is a self-annotation target.

Consult the stdlib-coverage skill before option 2 — it governs the
check loop and the `raises` integration with `no_exception`.

---

## Worked examples

### Example 1 — Simple math

No loop; just function-level contracts.

**Input:**
```python
def multiply_by_two(x: int) -> int:
    return x * 2
```

**Output:**
```python
#@ requires x >= 0
#@ ensures \result == x * 2
#@ assigns \nothing
def multiply_by_two(x: int) -> int:
    return x * 2
```

### Example 2 — Loops and accumulators

`while` loop with a counter that serves directly as the loop variant.

**Input:**
```python
def countdown_sum(n: int) -> int:
    total = 0
    while n > 0:
        total += n
        n -= 1
    return total
```

**Output:**
```python
#@ requires n >= 0
#@ ensures \result == n * (n + 1) / 2
#@ assigns \nothing
def countdown_sum(n: int) -> int:
    total = 0
    #@ loop invariant total >= 0
    #@ loop invariant n >= 0
    #@ loop invariant total + (n * (n + 1)) / 2 == \old(n) * (\old(n) + 1) / 2
    #@ loop variant n
    while n > 0:
        total += n
        n -= 1
    return total
```

### Example 6 — Linear search (flag + sentinel pattern)

When a loop body ends with a bare `return i` (outside any `if` block), the WhyML transpiler emits `!i` (type `int`) in a `unit` position, causing a type error. Introduce `found = -1` before the loop, replace `return i` with `found = i; i = n` to force loop exit, and `return found` after the loop.

**Input:**
```python
def linear_search(values, target):
    n = len(values)
    i = 0
    while i < n:
        if values[i] != target:
            i += 1
            continue
        return i
    return -1
```

**Output:**
```python
#@ requires True
#@ ensures \result >= -1
#@ assigns \nothing
def linear_search(values: list, target: int) -> int:
    n = len(values)
    i = 0
    found = -1
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant found >= -1
    #@ loop variant n - i
    while i < n:
        if values[i] != target:
            i += 1
            continue
        found = i
        i = n
    return found
```

> **More examples:** See `references/worked-examples-core.md` (for-loop conversion, continue/early-return, recursion, list summation — Examples 3–8c) and `references/worked-examples-advanced.md` (binary search, boolean flags, KMP — Examples 9–13).

---

## Reference files

For anything not covered above, consult these files in order of relevance to the task:

- **`references/forbidden-expressions.md`** — Complete list of NEVER rules for contract expressions: forbidden function calls, reserved names, type restrictions, pattern pitfalls, and WhyML type mismatches. Consult whenever writing any `#@` expression.

- **`references/validation-stack.md`** — Three-level validation-stack guide: IS/SR/TR rule tables and the practical decision checklist for syntax, static-semantics, and WhyML-generation failures.

- **`references/class-support.md`** — Class annotation rules: method contracts, `\old` usage, class invariants, multi-field records, multi-class files, and two complete class examples.

- **`references/worked-examples-core.md`** — Worked examples for core patterns: `for` loop conversion (Examples 3–5), factorial iterative/recursive (Example 7), list summation with weakened contracts (Examples 8, 8b, 8c).

- **`references/worked-examples-advanced.md`** — Worked examples for advanced patterns: binary search (Example 9), boolean-flag accumulators (Examples 10–12), KMP string search (Example 13).

- **`references/transpiler-limits.md`** — Body-code constraints: what the IR pipeline can lower to WhyML and what it cannot. Consult before annotating any function body that uses `return`, `None`, `raise`, `with`, dict access, ternary expressions, slice notation, `math.pi`, `sorted`/`set`, string methods, parameter mutation, nested early-return patterns, or anything beyond simple integer/list operations.

- **`references/solver-heuristics.md`** — Loop-invariant patterns for binary search, two-pointer, sliding window, multiplicative accumulators, binary flags + sentinels, conservation postconditions, and avoiding vacuous contracts.

- **`references/matrix-patterns.md`** — Matrix and 2D-array verification: the nonlinear-arithmetic problem, the linear-rewrite strategy, native 2D array support via `\length2d` / `\valid2d`, and five provable linear flat-matrix operations.

### Sibling skills (consult, do not duplicate)

- **`config/skills/pycsl-exception-model/SKILL.md`** — Phase 1 trigger
  table for `no_exception`. The authoritative source of truth for
  *which IR operation raises which Python exception, and which WhyML
  predicate discharges it*. Read before extending `no_exception`
  coverage.
- **`config/skills/pycsl-ub-catalog/SKILL.md`** — The five UB
  categories with detection mechanisms and escape annotations.
  Section 7 of this skill summarizes the patterns; the catalog has
  the full story.
- **`config/skills/pycsl-stdlib-coverage/SKILL.md`** — Governs the
  three-artefact discipline (`calls-english.md`, `calls-pycsl.md`,
  `src/pycsl_lib/`) and the discovery tool. Read before annotating
  code that calls a stdlib API for which no stub exists yet.

---

## Output requirements

Output ONLY the annotated Python code — no commentary, no explanation, no markdown fencing outside the code block.

**Every `if`, `elif`, and `else` block in the generated Python code MUST contain at least one statement.** An empty `if` body (a bare `if cond:` with no indented line below) is a Python syntax error (`expected an indented block`). Use `pass` as the body whenever the block has no logic to emit — for example:

```python
if radius < 0:
    pass
```

The output must include:

1. PEP 484 type hints on every parameter and return type.
2. All three function-level contracts (`#@ requires`, `#@ ensures`, `#@ assigns`) on every function, immediately before `def` with no blank lines.
3. `#@ \variant <expr>` on recursive functions; `#@ \diverges` when the function intentionally may not terminate; `#@ \trusted` when the body should be assumed correct without verification.
4. Loop-level contracts (`#@ loop invariant`, `#@ loop variant`) on every `for` and `while` loop, immediately before the loop keyword.
5. Class-invariant annotations (`#@ class invariant`) immediately before the `class` keyword when class-wide properties exist.

To verify only specific functions: `./pycsl --fun <name> file.py` — transitive call dependencies are included automatically.

## Real-World Modeling Patterns (from rclpy verification)

The following patterns were discovered during formal verification of the
ROS 2 `rclpy` library (97 goals, 6 files, 100% proof rate). They address
common challenges when verifying real-world Python code.

### File-level anchors

Every annotated file needs a sentinel line near the top so pycsl can
detect the annotation style:

- **`_ = 0  # anchor`** — for files without classes (standalone functions)
- **`""  # pycsl`** — for files with classes (class-centric models)

### Modeling complex classes as simplified models

Real-world classes often have 20+ methods and deep inheritance. PyCSL
verification targets a *model* of the class, not the full implementation:

1. Identify the **state fields** that carry safety-critical invariants
   (e.g., `_active`, `_count`, `_nanoseconds`)
2. Write a **class invariant** over those fields
3. Model only the **methods that mutate** invariant fields + key query
   methods
4. Use `#@ \trusted` for methods that call C extensions or external code

### Enum-as-integer modeling

Python `IntEnum` values should be modeled as plain `int` parameters with
range preconditions:

```python
#@ requires policy == 0 or policy == 1   # KEEP_ALL=0, KEEP_LAST=1
```

This keeps contracts in the integer domain that SMT solvers handle
efficiently.

### Transpiler workarounds (must know)

See `references/transpiler-limits.md` §12 for confirmed transpiler bugs:

- **TR-BUG-1 (float precision):** Large constants (>2^53) lose precision.
  Use `< 2^63` instead of `<= 2^63-1`.
- **TR-BUG-2 (purity bug):** Functions with `#@ raises` but no local
  variables are emitted as pure (`let function`) and Why3 rejects them
  as effectful. Add at least one local-variable assignment to force
  `let` (mutable) emission. *Especially important for `no_exception`
  interprocedural propagation* — when a callee with
  `raises { E -> P }` is invoked from a `no_exception E` caller,
  Module 6 wraps the call in `try ... with E -> absurd end`, which
  requires the callee to be effectful. Worked example:
  `test-suite/corpus/pycsl-reference/0383.py` (the local `m = n` is
  the TR-BUG-2 dodge).

### `no_exception` interprocedural-call patterns

When a function callable from `no_exception` contexts has any
`#@ raises` clause, follow this template:

```python
#@ requires True
#@ ensures \result == 256 / n
#@ raises ZeroDivisionError when n == 0
#@ assigns \nothing
def maybe_raise(n: int) -> int:
    m = n               # ← TR-BUG-2 dodge: force mutable emission
    if m == 0:
        raise ZeroDivisionError
    return 256 // m
```

The caller can then claim `no_exception ZeroDivisionError` and
discharge the propagated assertion via its own precondition:

```python
#@ requires n != 0
#@ ensures \result == 256 / n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def safe_caller(n: int) -> int:
    return maybe_raise(n)   # ← Module 6 wraps with try/with E -> absurd
```

### Simple class invariants (the trivial-prove pattern)

For pure data-carrier classes whose fields are non-negative integers,
the simplest provable invariant is `self.<field> >= 0`. This is the
seed pattern for self-annotation:

```python
#@ class invariant self.line >= 0
class PyCSLError(Exception):
    def __init__(self, message: str, *, filename: str = "",
                 line: int = 0, stage: str = "") -> None:
        super().__init__(message)
        self.filename = filename
        self.line = line
        self.stage = stage
```

PyCSL emits the invariant as a WhyML type invariant on the record;
the proof obligation is trivially valid because `line` only receives
a `: int = 0` default-or-caller-supplied value. Worked example:
`src/pycsl/errors.py` (the self-annotation suite seed —
`bin/run-self-annotation-suite.sh` proves it end-to-end).

## Glossary

Core terms used in this skill have canonical definitions in `../../../docs/glossary/`:
[ghost code](../../../docs/glossary/ghost-code.md) · [witness](../../../docs/glossary/witness.md) ·
[local reasoning](../../../docs/glossary/local-reasoning.md) ·
[solver budget](../../../docs/glossary/solver-budget.md) ·
[memory model](../../../docs/glossary/memory-model.md) ·
[loop invariant](../../../docs/glossary/loop-invariant.md)
