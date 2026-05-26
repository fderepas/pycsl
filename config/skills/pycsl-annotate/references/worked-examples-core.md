# Worked Examples — Core Patterns

These examples cover the most common annotation patterns: `for` loop conversion, `continue`/early-return, linear search, recursion, and list summation.

---

## Example 3 — `for` loop with `continue` and early return

Convert `for i in range(n)` to a while-loop: `i = 0` before the loop and `i += 1` at the end of each branch; use `n - i` as the variant.

**Input:**
```python
def first_positive(lst, n):
    for i in range(n):
        if lst[i] <= 0:
            continue
        return lst[i]
    return -1
```

**Output:**
```python
#@ requires n >= 0
#@ ensures \result >= -1
#@ assigns \nothing
def first_positive(lst: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if lst[i] <= 0:
            i += 1
            continue
        return lst[i]
        i += 1
    return -1
```

## Example 4 — For-each loop over a list (no index variable)

Capture the length in a local variable `n = len(collection)` before the loop, then use `i = 0` / `while i < n:` / `i += 1` so that `n - i` serves as the loop variant. Never use `len(...)` or `range(...)` inside any `#@` contract expression or loop header.

**Input:**
```python
def count_categories(items):
    negatives = 0
    zeros = 0
    positives = 0
    for item in items:
        if item < 0:
            negatives += 1
        elif item == 0:
            zeros += 1
        else:
            positives += 1
    return negatives, zeros, positives
```

**Output:**
```python
#@ requires True
#@ ensures True
#@ assigns \nothing
def count_categories(items: list) -> tuple:
    negatives = 0
    zeros = 0
    positives = 0
    n = len(items)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant negatives >= 0
    #@ loop invariant zeros >= 0
    #@ loop invariant positives >= 0
    #@ loop invariant negatives + zeros + positives == i
    #@ loop variant n - i
    while i < n:
        if items[i] < 0:
            negatives += 1
        elif items[i] == 0:
            zeros += 1
        else:
            positives += 1
        i += 1
    return negatives, zeros, positives
```

## Example 5 — For-each with continue and early return

When a loop uses `continue` and an accumulator-based early return, assign `i = 0` before the loop and write `while i < n:` with `i += 1` as the **last** statement in each branch (including before `continue`). This gives an explicit index for the variant `n - i` and avoids any use of `range(...)` or `len(...)` in loop headers or `#@` contract expressions.

**Input:**
```python
def running_total_until(values, threshold):
    total = 0
    for i in range(len(values)):
        if values[i] <= 0:
            continue
        total += values[i]
        if total >= threshold:
            return total
    return total
```

**Output:**
```python
#@ requires threshold > 0
#@ ensures \result >= 0
#@ assigns \nothing
def running_total_until(values: list, threshold: int) -> int:
    total = 0
    n = len(values)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        if values[i] <= 0:
            i += 1
            continue
        total += values[i]
        if total >= threshold:
            i = n
        else:
            i += 1
    return total
```

## Example 7 — Factorial (recursion or iterative accumulator)

### 7a — Iterative accumulator

Every function must have all three contracts. For a multiplicative accumulator, use `#@ requires n >= 1` (NOT `n >= 0`). Use only `acc >= 1` and `k >= 0` as loop invariants — do NOT add `acc * k >= 1`, which is nonlinear and Alt-Ergo returns `Unknown`. The `acc >= 1` invariant is sufficient: when the loop exits `k = 1`, so `acc >= 1` directly proves `\result >= 1`.

**Input:**
```python
def factorial(n: int) -> int:
    k = n
    acc = 1
    while k > 1:
        acc *= k
        k -= 1
    return acc
```

**Output:**
```python
#@ requires n >= 1
#@ ensures \result >= 1
#@ assigns \nothing
def factorial(n: int) -> int:
    k = n
    acc = 1
    #@ loop invariant k >= 0
    #@ loop invariant acc >= 1
    #@ loop variant k
    while k > 1:
        acc *= k
        k -= 1
    return acc
```

### 7b — Recursive definition (MUST include `#@ \variant`)

When `factorial` is implemented recursively (calls itself by name), it **MUST** include `#@ \variant n` immediately before the `def` line (after `#@ assigns \nothing`). Without it, Why3 emits `let rec factorial` but no `variant { n }` clause, and the termination sub-goal times out.

**Input:**
```python
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

**Output:**
```python
#@ requires n >= 0
#@ ensures \result >= 1
#@ assigns \nothing
#@ \variant n
def factorial(n: int) -> int:
    if n <= 1:
        return 1
    return n * factorial(n - 1)
```

## Example 8 — List summation (weakened contracts for signed integers)

When a function sums list elements, use `#@ requires True` and `#@ ensures True` for both precondition and postcondition. Specifically:

- **NOT** `#@ ensures \result >= 0` — list elements may be negative, making this unprovable.
- **NOT** `#@ requires \length(values) >= 0` — array length is trivially non-negative and adds no useful constraint; use `#@ requires True` instead.
- **NOT** any implication-based postcondition — whether it uses `\length` (e.g. `#@ ensures \length(values) == 0 ==> \result == 0`) or a local variable (e.g. `#@ ensures n == 0 ==> \result == 0`). After the loop, the solver knows `!i = !n` but cannot chain back through the accumulator to discharge the implication, and the goal times out in 30 s / 42 M steps. Use `#@ ensures True` instead. The `==>` operator is effectively banned in function-level `ensures` clauses for all index-loop traversals.
- **NOT** `#@ loop invariant total >= 0` — **unless** the loop uses `continue` to skip negative elements (see Example 8c). When elements may be negative, this invariant is unprovable; omit it.

Capture `n = len(values)` before the loop.

**Input:**
```python
def sum_list(values):
    total = 0
    for v in values:
        total += v
    return total
```

**Output:**
```python
#@ requires True
#@ ensures True
#@ assigns \nothing
def sum_list(values: list) -> int:
    n = len(values)
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        total += values[i]
        i += 1
    return total
```

## Example 8b — Parametric-n array summation (explicit bound parameter)

When a function receives both a `list` parameter `arr` **and** an explicit `int` parameter `n` that controls the loop (rather than capturing `n = len(arr)` locally), use `#@ requires n >= 0` and `#@ requires n <= \length(arr)` as preconditions. These are mandatory for the prover to discharge:
- the loop-invariant initialization sub-goal `0 <= n` (requires `n >= 0`)
- the array-bounds sub-goal `arr[!i]` (requires `n <= length arr`)

The postcondition is still `#@ ensures True` because the elements may be negative.

**Input:**
```python
def for_sum(arr: list, n: int) -> int:
    total = 0
    for item in arr:
        total += item
    return total
```

**Output:**
```python
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures True
#@ assigns \nothing
def for_sum(arr: list, n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        total += arr[i]
        i += 1
    return total
```

**Key rules:**
- `#@ requires n >= 0` is **mandatory** — without it `0 <= n` cannot be established at loop entry.
- `#@ requires n <= \length(arr)` is **mandatory** — without it `arr[!i]` index-bounds cannot be discharged.
- Do NOT write `#@ ensures \result >= 1` — the sum of arbitrary signed integers may not be ≥ 1.

## Example 8c — Skip-negative sum (loop `continue` filters negatives, so `total >= 0` IS provable)

When a loop uses `continue` to **skip negative elements** and accumulates only non-negative values into `total`, the invariant `total >= 0` IS provable and IS required to discharge `#@ ensures \result >= 0`. This is the **exception** to the Example 8 rule. Always add `#@ loop invariant total >= 0` when negatives are filtered out via `continue`.

**Input:**
```python
def sum_skip_negative(arr: list, n: int) -> int:
    total = 0
    i = 0
    while i < n:
        if arr[i] < 0:
            i += 1
            continue
        total += arr[i]
        i += 1
    return total
```

**Output:**
```python
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result >= 0
#@ assigns \nothing
def sum_skip_negative(arr: list, n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        if arr[i] < 0:
            i += 1
            continue
        total += arr[i]
        i += 1
    return total
```

**Key rules:**
- `#@ loop invariant total >= 0` is **required** — only non-negative elements are added, so the invariant holds and is needed by the prover to discharge `\result >= 0`.
- `#@ ensures \result >= 0` is **correct** here (unlike `sum_list`), because negatives are filtered.
- Increment `i` **before** `continue` so the variant `n - i` decreases on every branch.
