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

---

## 1. Return statements and `None`

**NEVER emit `return None`.** The IR emitter (Module5) maps every `ast.Constant` — including `None` — to `{"type": "Number", "value": <constant>}`, and Module6 calls `int(value)` on that field, which raises `TypeError` when the value is `null`. Use a bare `return` statement instead (semantically equivalent in Python), which makes Module5 emit `{"stmt": "Return", "value": null}` (no nested expression node) and Module6 skips it safely.

**NEVER use `None` as a sentinel value for numeric variables.** Same root cause: `ast.Constant(None)` maps to `{"type": "Number", "value": null}` and Module6 calls `int(null)`. Use `-1` as a sentinel for variables that only hold non-negative integers (e.g., write `last_end = -1` instead of `last_end = None`, and `if last_end < 0` instead of `if last_end is None`).

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

**NEVER use `raise` statements** in the annotated function body. Module5 has no handler for `ast.Raise`, so any `raise ValueError(...)` or similar statement causes the enclosing `if` block to emit `()` instead of a valid expression — and the function signature may drop parameters entirely. If a precondition is violated, express it only as a `#@ requires` contract; omit any runtime guard that raises an exception.

---

## 2. Control flow: `if`, `while`, conditions

**NEVER use subscript access inside a `while`-loop condition** (e.g., `while j >= 0 and arr[j] > key:`). The transpiler cannot lower compound boolean expressions containing a subscript inside the loop condition itself — this produces an empty condition (`while  do`) and a WhyML syntax error. Move the subscript check into the loop body: assign the element to a local variable before the condition test, or restructure the loop so the subscript check appears inside an `if` block in the body (set the index to `-1` or the loop bound to force early exit).

**NEVER use a compound boolean `while`-loop condition** (e.g., `while cond1 and cond2:` or `while flag == 1 and divisor * divisor <= n:`). The WhyML transpiler cannot lower compound boolean expressions in loop conditions and produces an empty `while  do`, causing a WhyML syntax error. Reduce the while condition to a single simple expression (e.g., `while flag == 1:`), then insert the extra guard as the **first `if` check inside the loop body** (e.g., `if divisor * divisor > n: flag = 0`). Adjust the loop variant to account for both the flag and the progress variable (e.g., `#@ loop variant (n - divisor + 1) + flag`).

**Crucially, also add `#@ loop invariant divisor <= n + 1` as the first loop invariant** (before all other invariants) to give the solver a direct linear upper bound on the progress variable. Without this bound, Alt-Ergo must use the nonlinear guard `divisor * divisor > n` to infer `divisor <= n`, which exceeds its timeout budget. With `divisor <= n + 1` stated explicitly, the variant non-negativity goal `(n - divisor + 1) + flag >= 0` becomes trivially provable from `divisor <= n + 1` and `flag >= 0`.

**NEVER use a compound boolean `if` condition** (e.g., `if cond1 and cond2:`) anywhere in an annotated function body. The same transpiler limitation that affects `while` conditions also applies to `if` conditions — a compound boolean `if` condition produces an empty `if  then` block and a WhyML syntax error. Fix: introduce a local integer variable (e.g., `balanced = 0`) before the compound test, then use two nested simple `if` blocks to set it:

```python
if ok == 1:
    if depth == 0:
        balanced = 1
```

Use `balanced` in the return or subsequent logic. Each `if` condition must be a single atomic comparison.

---

## 3. Loops and iteration

**`for i in range(n)` is supported** — the transpiler emits an integer counter loop. Annotate with `#@ loop invariant` and `#@ loop variant` immediately before the `for` keyword, just like `while` loops. The loop variable `i` is the counter. **Multi-argument `range(start, stop)` is NOT supported** — use an explicit `while` loop for those cases.

**Subscript access (`arr[idx]`) in while-loop bodies is supported** — the IR pipeline translates `values[i]` into `values[!i]` in WhyML (mutable array read). When iterating over a list with an explicit index variable, it is correct to write `if values[i] < 0:` inside a while-loop body. The local index variable (`i`) will be automatically dereferenced.

**Subscript assignment (`arr[i] = value`) is supported** — the IR pipeline emits `arr[i] <- value` in WhyML for any `arr[i] = expr` in the body. This is valid when `arr` is a `list`-typed parameter. Use it freely for in-place array mutation. Annotate the function's `#@ assigns` accordingly (e.g., `#@ assigns \nothing` is still valid if the mutation is only to a local-scope array; use the parameter name if a caller-visible array is mutated).

---

## 4. Parameter mutation

**NEVER mutate a function parameter directly** — neither inside a loop nor via any conditional assignment before the loop (e.g., `n -= 1` where `n` is a function parameter, or `if a < 0: a = -a` before a while-loop). Module6's mutability analyzer marks **any** parameter that is assigned **anywhere** in the function body as a `ref` and omits it from the WhyML function signature, making the function unverifiable.

Instead, introduce a separate local variable before the loop, use that variable for all mutations and loop operations, and keep the original parameter read-only. For `factorial`, annotate as:

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

Use `x` and `y` for all mutations, loop invariants (e.g., `#@ loop invariant x >= 0`), and the return statement — never reassign `a` or `b` anywhere.

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

**NEVER use slice notation** (e.g., `values[1:]`, `lst[i:]`). The IR pipeline has no handler for Python slice expressions and will produce invalid WhyML. Iterate with explicit indices instead.

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
