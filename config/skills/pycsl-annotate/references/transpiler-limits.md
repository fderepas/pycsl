# Transpiler limits — what the IR pipeline can and cannot lower

This file documents the **body-code** constraints imposed by the PyCSL IR pipeline (Module5) and the WhyML transpiler (Module6). These rules apply to the Python statements *inside* a function body, not to `#@` contract expressions. For the contract-expression restrictions, see Section 4 of `SKILL.md`.

When in doubt, prefer the simplest form that the transpiler can handle. Many limitations have a documented workaround below.

## Table of contents

1. [Return statements and `None`](#1-return-statements-and-none)
2. [Control flow: `if`, `while`, conditions](#2-control-flow-if-while-conditions)
3. [Loops and iteration](#3-loops-and-iteration)
4. [Parameter mutation](#4-parameter-mutation)
5. [Built-in functions and operators](#5-built-in-functions-and-operators)
6. [Strings, lists, dicts, slices](#6-strings-lists-dicts-slices)
7. [Recursion and termination](#7-recursion-and-termination)
8. [Type and signature constraints](#8-type-and-signature-constraints)
9. [Reserved keywords](#9-reserved-keywords)
10. [Ghost variable types — Why3 `use` dependencies](#10-ghost-variable-types--why3-use-dependencies)
11. [Escape hatch: facts SMT cannot discharge alone](#11-escape-hatch-facts-smt-cannot-discharge-alone)

---

## 1. Return statements and `None`

**NEVER emit `return None`.** The IR emitter (Module5) maps `None` to `{"type": "None"}` which Module6 renders as `0`. Use a bare `return` statement instead (semantically equivalent in Python), which makes Module5 emit `{"stmt": "Return", "value": null}` (no nested expression node) and Module6 skips it safely.

**`None` as a value is supported** — `None` appearing in assignments or expressions maps to integer `0` in WhyML. However, avoid using `None` as a sentinel for numeric variables when the function relies on distinguishing `None` from `0`. Use `-1` as a sentinel for variables that only hold non-negative integers.

**NEVER use `return expr` inside an `if` block that is nested inside a loop body.** Module6 emits a lone `if-then` block (without `else`) as type `()`, but a bare dereference such as `!total` has type `int`, producing a fatal type mismatch at the Why3 type-checker. When a loop needs an early exit after an accumulator update, **set the index variable to `n`** (the loop bound) to force the loop condition false and let the function return normally after the loop. Replace `if total >= threshold: return total` inside a loop with `if total >= threshold: i = n` (plus `else: i += 1` so the index still advances on the non-exit path), and keep the final `return total` after the loop.

**NEVER use `return expr` inside a bare `if` block (no `else`) at the function's top level.** Module6 emits a lone `if-then` expression whose `then` branch has type `int` (not `unit`), causing a type mismatch in statement position. Always structure recursive base cases as a complete `if-else` chain. Rewrite a standalone `if condition: return base_value` (followed later by `return recursive_call(...)`) as:

```python
if condition:
    return base_value
else:
    return recursive_call(...)
```

For `factorial`, this means writing `if n <= 1: return 1` followed by `else: return n * factorial(n - 1)` — not a bare early-return `if`.

**NEVER use `return expr` directly in a while-loop body outside any `if` block.** Module6 emits the loop body as a sequence of `unit`-typed statements; a bare dereference such as `!i` has type `int`, causing a fatal 'expected type int but got ()' error. This commonly arises in linear-search patterns where `return i` sits at the end of the loop body after an `if … continue` guard. Fix: introduce a `found` variable initialised to `-1` before the loop, replace `return i` with `found = i` followed by `i = n` (to force the loop condition false), and place the single `return found` **after** the loop. See Example 6 in `SKILL.md`.

**`raise` statements are supported** — `raise ExcType(...)` in the function body is transpiled to `raise ExcType` in WhyML, with the exception type auto-declared. Use `#@ raises ExcType when <cond>` for exceptional postconditions (see annotations.md §2.1.9).

---

## 2. Control flow: `if`, `while`, conditions

**Compound boolean `while`-loop conditions are supported** (e.g., `while j >= 0 and acc[j] > key:`). Module5 now handles `ast.BoolOp` by folding the operand list into a left-associative `BinOp` tree with op `"and"` or `"or"`, which Module6 maps to `&&` and `||` in WhyML. You may write natural compound conditions directly.

**When a nonlinear guard appears in a compound `while` condition** (e.g., `while flag == 1 and divisor * divisor <= n:`), consider whether the solver can discharge the loop variant. If the variant involves a term bounded by the nonlinear guard, add an explicit linear loop invariant (e.g., `#@ loop invariant divisor <= n + 1`) to give the solver a direct upper bound. With the linear invariant stated explicitly, the variant non-negativity goal becomes trivially provable without relying on the nonlinear guard.

**Compound boolean `if` conditions are supported** (e.g., `if cond1 and cond2:`). Module5 handles `ast.BoolOp` in all expression positions, including `if` conditions.

---

## 3. Loops and iteration

**`for i in range(n)` is supported** — the transpiler emits an integer counter loop. Annotate with `#@ loop invariant` and `#@ loop variant` immediately before the `for` keyword, just like `while` loops. The loop variable `i` is the counter. **Multi-argument `range(start, stop)` is NOT supported** — use an explicit `while` loop for those cases.

**Subscript access (`arr[idx]`) in while-loop bodies is supported** — the IR pipeline translates `values[i]` into `values[!i]` in WhyML (mutable array read). When iterating over a list with an explicit index variable, it is correct to write `if values[i] < 0:` inside a while-loop body. The local index variable (`i`) will be automatically dereferenced.

**Subscript assignment (`arr[i] = value`) is supported** — the IR pipeline emits `arr[i] <- value` in WhyML for any `arr[i] = expr` in the body. This is valid when `arr` is a `list`-typed parameter. Use it freely for in-place array mutation. Annotate the function's `#@ assigns` accordingly (e.g., `#@ assigns \nothing` is still valid if the mutation is only to a local-scope array; use the parameter name if a caller-visible array is mutated).

---

## 4. Parameter mutation

**As of 2026-05-27, parameter mutation is supported.** Module6 now promotes a mutated parameter to a ref via `let a = ref a in` shadowing inside `_emit_body_code`, keeping the parameter in the WhyML function signature (see `_build_param_list`). Tuple-unpack on parameters works: `def gcd(a, b): while b != 0: a, b = b, a % b; return a` transpiles correctly. The function-level `assigns \nothing` clause is also respected (parameter mutation does not violate frame conditions because the parameters are local copies semantically).

**Loop-invariant pragmatics: use ghost snapshots, not `\old(...)`.** When the loop invariant needs to refer to the parameter's entry value, do NOT write `\old(a)` — the emitted Why3 expression is `old !a` (`old` over a deref of the shadowed ref), which Alt-Ergo can struggle to discharge (postconditions in the Euclidean GCD case time out at 30s). Capture the entry values via ghost variables at function entry and use those names in the invariant:

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

Ensures clauses can still reference `a, b` directly (at the contract scope, parameters refer to their entry values regardless of body mutation). Worked example: `test-suite/corpus/pycsl-reference/0352.py`.

**When you should still avoid parameter mutation:** if the parameter is typed `List[T]` / `Set[T]` / `Dict[K, V]` (i.e., not a plain `int` / `bool`), the `let a = ref a in` shadow would wrap an `array int` or `map int (option int)` in a Why3 ref — Why3 rejects mutable arrays in refs due to region/linearity rules. For collection-typed parameters, still use the local-variable pattern below.

### Fallback pattern (for non-int params, or when ghost snapshots aren't worth it)

Introduce a separate local variable before the loop, use that variable for all mutations and loop operations, and keep the original parameter read-only. For `factorial`, annotate as:

```python
k = n
#@ loop invariant k >= 0
while k > 1:
    acc *= k
    k -= 1
```

For a two-parameter GCD-style function `gcd(a, b)` that needs absolute values and then iteratively updates the pair, **do NOT use ternary/conditional expressions** like `x = a if a >= 0 else -a`. The transpiler lowers such ternaries into if-else blocks that scope `x` as a branch-local binding, leaving it unbound at the while loop. Instead, initialize the local variables unconditionally first, then apply sign corrections with simple if-statements:

```python
x = a
y = b
if x < 0: x = -x
if y < 0: y = -y
while y > 0:
    temp = x % y
    x = y
    y = temp
return x
```

Use `x` and `y` for all mutations, loop invariants (e.g., `#@ loop invariant x >= 0`), and the return statement.

(Note: as of 2026-05-27 you CAN reassign `a` or `b` directly — see the ghost-snapshot pattern above. The fallback above remains useful for collection-typed parameters or when you want the simplest possible loop-invariant prover obligations.)

---

## 5. Built-in functions and operators

**`len(x)` is supported and maps to `(length x)` in WhyML.** Assigning the length of a list parameter to a local variable (`n = len(values)`) is the correct pattern. The IR pipeline emits `length values` using `array.Array`. Never substitute `len()` with a manual counter or an extra function parameter just to avoid using it.

**`min(a, b)` and `max(a, b)` are supported** — they map to `(Int.min a b)` / `(Int.max a b)` in WhyML. Always use exactly two arguments (single-argument `min(list)` is NOT supported).

**The `/` (true-division) operator is supported and maps to WhyML `div` (Euclidean integer division).** Both `/` and `//` in the function body produce `div` in the generated WhyML. The module preamble includes `use int.EuclideanDivision` so `div` is always in scope. Either operator may be used for integer division.

**Use `//` (floor-division) freely** — the transpiler emits it as a prefix application `(div {left} {right})`. Why3's `int.EuclideanDivision` theory exposes `div` as a prefix function; the transpiler emits `(div {left_whyml} {right_whyml})` rather than the infix form. This prefix notation is always unambiguous — there is no `!`-precedence issue to work around. For example, `mid = (left + right) // 2` correctly generates `let mid = ref (div (!left + !right) 2) in`.

**NEVER use `math.pi`, `pi`, or any irrational constant** from Python's `math` module in an annotated function body. The WhyML transpiler has no counterpart for `pi` and will produce a proof failure. If a function computes with `pi` (e.g., `circle_area`), rewrite the body to use only integer arithmetic: return `radius * radius` and document in a comment that the caller scales by pi. Remove any `from math import pi` (or `import math`) import from the annotated output, and use `#@ ensures \result >= 0` as the postcondition instead of an equality involving `pi`.

**NEVER use the `sorted()` or `set()` built-ins** (e.g., `sorted(set(values))`). The IR pipeline cannot lower these to WhyML. When deduplication or sorting is required, implement the logic explicitly with a while-loop. If the function only needs to iterate over unique elements, restructure it to accept a pre-deduplicated list parameter instead.

---

## 6. Strings, lists, dicts, slices

**`str`-typed parameters are supported and map to WhyML `string`.** Functions with `str` parameters or `str` return types correctly emit `(param: string)` and `: string` in the generated WhyML. String literals `"hello"` can be used in contracts (`#@ ensures \result == "hello"`) and function bodies. **However,** string method calls (e.g., `text.lower()`, `ch.isalnum()`, `text.strip().split()`, `''.join(letters)`) are **NOT supported** — only equality comparison and return of string values are available.

**List mutation calls and list concatenation are NOT supported.** The IR pipeline cannot lower list literals used as accumulators (e.g., `letters = []`) or list concatenation expressions (e.g., `letters + [ch]`). For complex string or list processing, rewrite the function to accept pre-processed `int` or `list` parameters instead.

**NEVER call methods on list parameters inside the annotated function body** (e.g., `log.append(event_len)`, `items.sort()`). Module6 (`_stmts_to_whyml`) has no handler for bare method-call expression-statements. When such a call appears between a `let x = ref … in` declaration and the next expression, Module6 emits an empty code string and the semicolon sequencer prepends a spurious `;\n` before the next expression — producing invalid WhyML like `let n = ref (length log) in\n;\n(!n + 1)`. **Remove any mutation calls on list parameters from the annotated body**. The `#@ assigns` contract already captures the frame condition; the body only needs to compute and return the value.

**NEVER use `if not <list_var>:` as an emptiness guard for list/sequence parameters.** In WhyML a list parameter is typed `array int`, and `not` cannot be applied to an array — doing so causes a fatal type mismatch. Instead, assign `n = len(list_var)` before the loop, test emptiness with `if n == 0:`, and iterate using an index-based `while i < n:` loop accessing elements via `list_var[i]`.

**NEVER use slice notation with step** (e.g., `values[::2]`, `lst[i:j:k]`). Only simple two-argument slices `arr[lo:hi]` are supported — the transpiler emits an abstract `array_slice` function call. Step-based slicing has no handler.

**List comprehensions are CONTENT-faithful for simple element shapes** (cleared-array.md S1–S4 + S2). `[x for x in a]`, `[x + 1 for x in a]` (identity / pure-int `+ - *` arithmetic), and `[p.x for p in a]` / `[p.x + p.y for p in a]` (FIELD PROJECTIONS over the loop target) all carry a per-index law you can prove: `\result[k] == a[k]`, `\result[k] == a[k] + 1`, `\result[k] == a[k].x`, `\result[k] == a[k].x + a[k].y`, each with `\length(\result) == \length(a)`. To CONSUME a projection law, write `a[k].field` in the contract (the subscript-then-projection atom, §3.1.4c). A filter `[x for x in a if …]` keeps only `\length(\result) <= \length(a)` (surviving elements are not at their source indices). Opaque residuals — do NOT claim per-index content for: call comprehensions `[g(x) for x in a]` (a module function is not usable in a logic term), subscript projection `[x[k] for x in a]` (nested lists collapse to `array int`), string/seq elements, multi-generator, and set/dict comprehensions.

**NEVER use string-literal subscript keys** (e.g., `row["id"]`, `data["name"]`). Dict-style subscript access is not supported in WhyML. When a function receives a dict-like record, rewrite it to accept the individual fields as separate integer (or list) parameters. For example, replace `def process(row): return row["id"]` with `def process(row_id: int) -> int: return row_id`.

**NEVER call dict methods** such as `.get(key, default)` (e.g., `counts.get(word, 0)`). The IR pipeline has no handler for dict method calls and will produce invalid WhyML. Refactor such functions to avoid dicts entirely — use integer accumulators or list parameters instead. Replace `counts.get(word, 0) + 1` with a simple integer counter incremented in a while-loop body.

---

## 7. Recursion and termination

**Direct recursion is supported when annotated with `#@ \variant <expr>`.** The pipeline emits `let rec f` and a `variant { expr }` clause in WhyML. The variant expression must be a non-negative integer that strictly decreases on each recursive call. Always use a complete `if-else` for the base case (not a bare `if` with early return):

```python
#@ requires n >= 0
#@ ensures \result >= 1
#@ \variant n
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)
```

If recursion is used **without** `#@ \variant`, the pipeline auto-detects the self-call and still emits `let rec`, but Why3 will warn about unproven termination.

If the function intentionally does not terminate, use `#@ \diverges` instead.

When no variant annotation is desired, rewrite recursive algorithms as explicit iterative `while` loops with an accumulator.

---

## 8. Type and signature constraints

**`list` parameter type hints are required for sequence arguments** — any function parameter that holds a sequence (e.g., `values: list`) will be lowered to `array int` in the WhyML function signature. Always annotate list/sequence parameters with `: list` so the IR pipeline emits the correct WhyML type.

**NEVER annotate a function with `-> list` as the return type.** The WhyML transpiler always infers the return type of every function as `int`. Returning an `array int` (a list parameter) where `int` is expected causes a fatal type mismatch in the generated WhyML. This commonly occurs in in-place sorting or mutation functions (e.g., `insertion_sort`) that end with `return values`.

Fix: always declare the return type as `-> int`, drop any `return <list_param>` at the end of the function body, and instead `return 0`. Update the postcondition to `#@ ensures \result == 0`.

---

## 9. Reserved keywords

**NEVER name a local accumulator variable `result`.** In WhyML, `result` is a reserved keyword bound to the function's return value inside `ensures` clauses. The transpiler emits `let result = ref 1 in`, which shadows the built-in `result` binding used by the postcondition `ensures { (result >= 1) }` — causing Alt-Ergo to see the postcondition as referencing the mutable ref rather than the actual return value and report 'Unknown'. Always use a different name such as `acc`, `product`, or `total` for any local accumulator.

**NEVER use `goal` as a function parameter name.** In WhyML, `goal` is a reserved keyword used to declare proof obligations. Using it as a parameter name in the generated function signature causes a Why3 syntax error. Rename any function parameter named `goal` to a non-reserved alternative such as `target`, `dest`, or `end_node`, and update all references in `#@ requires`, `#@ ensures`, loop invariants, and the function body accordingly.

**NEVER use `val` as a function parameter name.** In WhyML, `val` is a reserved keyword used to declare program functions. Using it as a parameter name (e.g., `(val: int)`) produces a Why3 syntax error at the function signature. Rename any function parameter named `val` to a non-reserved alternative such as `v`. For example, `counter_value(val: int) -> int` must be written as `counter_value(v: int) -> int` with `#@ ensures \result == v`, and `counter_increment(val: int, amount: int) -> int` as `counter_increment(v: int, amount: int) -> int` with `#@ ensures \result == v + amount`.

---

## 10. Ghost variable types — Why3 `use` dependencies

Ghost variables declared with `#@ ghost name : TYPE = expr` require specific Why3 library modules to be loaded in the module preamble. The transpiler adds these automatically when it detects the corresponding ghost type. The table below documents which libraries are required and any SMT-performance notes:

| Ghost type | Declared as | Required `use` directives | Notes |
|---|---|---|---|
| (default) | `#@ ghost x = 0` | none | Emits `let ghost x = ref 0 in` — pure integer, no extra library |
| `string` | `#@ ghost s : string = "..."` | `use string.String` | Supports `^` (concat), `\str_length`, `\str_sub`. Strings are native in Why3. |
| `array` | `#@ ghost arr : array = \make(n, v)` | `use array.Array` | Hoare/concurrent memory models only; emits `Array.make n v`. Typed/store models use `int_mem` heap — do not use ghost array type with those models. `\copy(arr)` and `\copy_range(arr, lo, hi)` have the same restriction (emit `Array.copy`/`Array.sub` which expect `array int`, not `loc`). |
| `ghost_dict` | `#@ ghost d : ghost_dict = \empty_map` | `use map.Map`, `use map.Const`, `use option.Option` | Emits `Map.const (None: option int)`. `\map_get(d, k)` emits `match Map.get !d k with \| Some v -> v \| None -> 0 end`. `\has_key(d, k)` emits `Map.get !d k <> None`. `\map_remove(d, k)` emits `Map.set !d k None`. `\map_eq(d1, d2)` emits a `forall` quantifier — restrict to shallow comparisons in loop invariants. |
| `ghost_list` | `#@ ghost l : ghost_list = \nil` | `use list.List`, `use list.Length`, `use list.Nth`, `use list.Mem`, `use list.Append` | Emits `Nil`. `\hd`/`\tl` on empty list produce `absurd` — ensure preconditions guard emptiness. |
| `ghost_set` | `#@ ghost s : ghost_set = \set_empty` | `use map.Map`, `use map.Const` | Emits `Map.const false`. `\set_union`/`\set_inter`/`\set_diff` are represented as functional lambdas (`fun k -> ...`); restrict operands to **bounded integer ranges** for best SMT performance. `\set_card` requires a custom Why3 preamble — avoid in proof contexts. |
| `tuple2` | `#@ ghost p : tuple2 = \mktuple(a, b)` | none | Native Why3 tuple `(int, int)`; `\fst`, `\snd`, `\proj(p, 0)`, `\proj(p, 1)` are destructuring patterns. |
| `tuple3` | `#@ ghost t : tuple3 = \mktuple(a, b, c)` | none | Native Why3 tuple `(int, int, int)`; `\proj(t, 0..2)`. |
| `tuple4` | `#@ ghost t : tuple4 = \mktuple(a, b, c, d)` | none | Native Why3 tuple `(int, int, int, int)`; `\proj(t, 0..3)`. |

---

## 11. Escape hatch: facts SMT cannot discharge alone

Some specifications hinge on mathematical facts Alt-Ergo and Z3 cannot
discover unaided — Euclidean identities, divisibility lemmas, transcendental
relations, group-theoretic properties. When this happens, the historical
options were poor: either weaken the contract until SMT could handle it, or
mark the function `#@ \trusted` and lose the proof entirely.

The supported way out is the **`#@ proof`** directive
(`annotations.md §2.1.12`), which imports a Rocq or Lean theorem as a
Why3 axiom in the generated preamble. Used in pairs, it implements the
**"Rocq + Lean as Cross-Validated Spec Sources"** pattern: when both
`#@ proof rocq <q>` and `#@ proof lean <q>` cite the same
`pycsl_target`, the `proof2why3 cross-check` tool extracts both theorem
statements, canonicalizes them (alpha-normalize, AC-flatten, `nat`/`Nat`
→ `int + ≥ 0`), and refuses to emit the axiom unless the two formalisms
agree. The Why3 axiom is then trusted because **two independent proof
kernels** independently verified the same statement.

**When to reach for this:**

- A divisibility / modular-arithmetic postcondition that no SMT prover
  closes within a minute (e.g., GCD, CRT, Bezout).
- A property whose proof requires structural induction that `intros; lia`
  cannot replay.
- Any fact for which a stdlib lemma exists in Rocq/Lean but no equivalent
  in Why3's `int.*` theories.

**When NOT to reach for this:**

- The contract is just stated wrong (missing precondition, wrong sign).
  Strengthen the contract first.
- The fact is linear arithmetic — `\result == \old(...) + amount` should
  go through directly; if it doesn't, the bug is upstream.
- You haven't actually written and machine-checked the cited theorem yet.
  `#@ proof` referencing a non-existent qualname is no safer than
  `#@ \trusted`, just more verbose. Run `pycsl --audit-proof <file>` to
  fail when the cited theorem is missing or outside the declared
  namespace.

**Worked example:** `test-suite/corpus/pycsl-reference/0342.py` (Euclidean
GCD) with six cross-validated axioms (`gcd_result_nonneg`,
`gcd_result_positive`, `gcd_divides_a`, `gcd_divides_b`, `gcd_0`,
`gcd_step`). Both `0342.proofs/rocq/gcd.v` and `0342.proofs/lean/Gcd.lean`
machine-check the same six statements; the WhyML preamble then carries
the axioms unconditionally, and Alt-Ergo discharges all four
divisibility postconditions in single-digit seconds.

**Annotator agents MUST NOT generate `#@ proof` directives**
unless the cited theorems already exist and `proof2why3 cross-check`
reports `reconciled` status. Adding the directive without the matching
proof artifacts breaks the trust chain silently.

### `\proj` index constraints

- `\proj(t, idx)` — `idx` **must be an integer literal** (0, 1, 2, or 3). A variable index is rejected by Module4 with a semantic error ("dynamic projection is not supported").
- The index must be within the arity of the declared tuple type. Using `\proj(p, 2)` on a `tuple2` variable silently generates incorrect WhyML (a three-element destructuring pattern where only two exist); Module4 does not currently enforce arity bounds.

### Ghost string augmented assignment

**NEVER use `#@ ghost s += expr` when `s` is a ghost string variable.** The `+=` shorthand is defined only for numeric (`int`) ghost variables. For string concatenation, use the `^` operator: `#@ ghost s = s ^ "suffix"`. Using `+=` on a string ghost is rejected at Module4 with a semantic error.

### Augmented assignment shorthands

The following `+=` shorthands are supported and emit idiomatic Why3 operations:

| Pattern | Ghost type | Emitted Why3 |
|---|---|---|
| `#@ ghost x += n` | `int` (default) | `ghost x := !x + n` |
| `#@ ghost l += v` | `ghost_list` | `ghost l := Cons v !l` (prepend) |
| `#@ ghost s += v` | `ghost_set` | `ghost s := Map.set !s v true` (insert) |
| `#@ ghost d += \mktuple(k, v)` | `ghost_dict` | `ghost d := Map.set !d k (Some v)` (insert/update) |

---

## 12. Known transpiler bugs (with workarounds)

These are confirmed bugs discovered during formal verification of the
ROS 2 `rclpy` library. Until they are fixed, use the workarounds below.

### TR-BUG-1: Float precision loss in large integer constants

The transpiler converts contract constants through `float` internally.
Integer constants larger than 2^53 lose precision:

```
int(float(9223372036854775807))  →  9223372036854775808   # 2^63 - 1 → 2^63
```

**Impact:** A contract `#@ requires n <= 9223372036854775807` (2^63-1) is
compiled to `n <= 9223372036854775808` (2^63) in WhyML — the boundary
shifts by one.

**Workaround:** Use constants that survive float round-trip. Replace
`>` / `<=` with `>=` / `<` against the next representable value:

```python
# WRONG: 2^63-1 loses precision → becomes 2^63 in WhyML
#@ requires nanoseconds <= 9223372036854775807

# CORRECT: 2^63 survives float round-trip, use < instead of <=
#@ requires nanoseconds < 9223372036854775808
```

Both express the same mathematical constraint (`ns ≤ 2^63 - 1` ≡
`ns < 2^63`), but only the second compiles correctly.

### TR-BUG-2: Pure-function emission for functions with `raises`

When a function has `#@ raises ExcType when <cond>` but contains no local
variable assignments in its body, the transpiler emits it as
`let function` (pure) in WhyML. The `raises` clause is effectful and
requires `let` (not `let function`). Why3 rejects the result.

**Impact:** A simple validator like:

```python
#@ raises ValueError when x < 0
#@ assigns \nothing
def check_positive(x: int) -> int:
    if x < 0:
        raise ValueError
    return x
```

fails at the Why3 level because the function is emitted as pure but
declares an exception.

**Workaround:** Add a local variable assignment to force mutable mode:

```python
#@ raises ValueError when x < 0
#@ assigns \nothing
def check_positive(x: int) -> int:
    v = x                  # forces `let` (mutable) emission
    if v < 0:
        raise ValueError
    return v
```
