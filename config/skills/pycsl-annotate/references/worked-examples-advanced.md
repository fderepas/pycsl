# Worked Examples — Advanced Patterns

These examples cover advanced annotation patterns: binary search, boolean-flag accumulators, and KMP string search.

---

## Example 9 — Binary search (two-pointer loop, upper-bound invariant required)

When a loop uses two counters `left` and `right` with guard `left <= right` and accesses `arr[mid]` where `mid = (left + right) // 2`, you **must** provide an explicit upper bound on `right`. Without `right < n`, Alt-Ergo cannot discharge the array-bounds safety VC for `arr[mid]` and will time out.

Always capture the length as `n = len(sorted_values)` before the loop, then add all four invariants as **separate** lines. Do NOT write a compound clause like `left <= right` in any invariant (it fails when the array is empty).

**Output:**
```python
#@ requires True
#@ ensures \result >= -1
#@ assigns \nothing
def binary_search(sorted_values: list, target: int) -> int:
    n = len(sorted_values)
    left = 0
    right = n - 1
    found = -1
    #@ loop invariant 0 <= left
    #@ loop invariant left <= n
    #@ loop invariant right >= -1
    #@ loop invariant right < n
    #@ loop invariant found < n
    #@ loop variant right - left + 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_values[mid] == target:
            found = mid
            left = right + 1
        elif sorted_values[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return found
```

**Key rules for binary-search loops:**
- The `right < n` invariant is **mandatory** — Alt-Ergo cannot derive the array-bounds goal `mid <= n - 1` without the explicit upper bound.
- The `found < n` invariant is also **mandatory** whenever the loop writes `found = mid`. Without it, the solver cannot bound `found` below `n` after the assignment `found = mid = (left + right) // 2`, so it cannot discharge the postcondition `\result <= \length(sorted_values) - 1` and will time out.

---

## Example 10 — Boolean-flag accumulator (sorted-check pattern)

When a function traverses a list to check a property (e.g., `is_sorted_non_decreasing`) and uses an `acc` variable as a 0/1 flag, **always use `acc` in the loop invariant — never use `result`**. The variable `result` does not exist in the function body; `acc` is the real local variable.

**Input:**
```python
def is_sorted_non_decreasing(values):
    for i in range(1, len(values)):
        if values[i - 1] > values[i]:
            return False
    return True
```

**Output:**
```python
#@ requires True
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def is_sorted_non_decreasing(values: list) -> int:
    n = len(values)
    i = 0
    acc = 1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc == 1 or acc == 0
    #@ loop variant n - i
    while i < n - 1:
        if values[i] > values[i + 1]:
            acc = 0
            i = n
        else:
            i += 1
    return acc
```

**Key rule:** The loop invariant **must reference `acc`** (the actual accumulator variable declared in the function body), not `result` (which is not a local variable — it is only meaningful in `ensures` as `\result`). Writing `#@ loop invariant result == 0 or result == 1` will cause an unbound-variable error in the WhyML transpiler.

---

## Example 11 — Boolean-flag accumulator with local item variable (`any_negative` pattern)

When a function contains `return True` (not `return False`) inside the loop and additionally reads the element into a local variable before the `if`, apply the same flag+sentinel pattern as Example 10 but with `acc = 0` as the default (opposite of the early-exit value `1`).

**Input:**
```python
def any_negative(arr: list, n: int) -> bool:
    for item in arr:
        if item < 0:
            return True
    return False
```

**Output:**
```python
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def any_negative(arr: list, n: int) -> bool:
    i = 0
    acc = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc == 0 or acc == 1
    #@ loop variant n - i
    while i < n:
        item = arr[i]
        if item < 0:
            acc = 1
            i = n
        else:
            i += 1
    return acc
```

**Key rules for this pattern:**
- `acc = 0` (not `acc = 1`) before the loop because `return False` is the post-loop default.
- `acc = 1` (not `True`) inside the `if` branch — always use the integer literal `1`, not the Python keyword `True`.
- `#@ loop invariant acc == 0 or acc == 1` is **required** to prove `\result == 0 or \result == 1`; omitting it causes Why3 to reject the ensures clause.
- `return acc` (not `return False`) after the loop — forgetting this leaves the body ending with a constant instead of `!acc`, making the early-exit assignment ineffective.

---

## Example 12 — Boolean-flag accumulator starting at 1 (`all_positive` / `none_zero` pattern)

When a function starts `acc = 1` (assumes "true" by default and sets `acc = 0` on an early-exit condition), the postcondition MUST still be `#@ ensures \result == 0 or \result == 1` — **not** `#@ ensures True` and not the reversed `#@ ensures \result == 1 or \result == 0`.

**Critical rules:**
- The contract order is always **requires → ensures → assigns**. Never place a `#@ requires` after `#@ assigns`.
- The `ensures` disjunction must be `\result == 0 or \result == 1` (0 first).
- The **loop invariant** disjunction must lead with the initial value of `acc`: use `acc == 1 or acc == 0` when `acc` starts at `1`, and `acc == 0 or acc == 1` when `acc` starts at `0`. Putting the wrong value first makes Why3 attempt an unsatisfiable equality as its first subgoal and times out after 30 s.
- `#@ ensures True` is **wrong** for a boolean-flag function — it forces the prover to abandon the `acc` invariant context and leaves the VC unproven.

**Input (`all_positive`):**
```python
def all_positive(arr: list, n: int) -> bool:
    for item in arr:
        if item <= 0:
            return False
    return True
```

**Output:**
```python
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def all_positive(arr: list, n: int) -> int:
    i = 0
    acc = 1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc == 1 or acc == 0
    #@ loop variant n - i
    while i < n:
        item = arr[i]
        if item <= 0:
            acc = 0
            i = n
        else:
            i += 1
    return acc
```

**Input (`none_zero`):**
```python
def none_zero(arr: list, n: int) -> bool:
    for item in arr:
        if item == 0:
            return False
    return True
```

**Output:**
```python
#@ requires n >= 0
#@ requires n <= \length(arr)
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def none_zero(arr: list, n: int) -> int:
    i = 0
    acc = 1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant acc == 1 or acc == 0
    #@ loop variant n - i
    while i < n:
        item = arr[i]
        if item == 0:
            acc = 0
            i = n
        else:
            i += 1
    return acc
```

## Example 13 — KMP string search (two-pointer loops, failure-table, array-bounds invariants)

KMP-style algorithms use two index variables (`i` over text, `k` over pattern) in nested loops. Five annotation rules must be observed:

1. `count_occurrences` needs `#@ requires \length(pattern) >= 1` to prove `m >= 1` at loop initialization. If the outer loop also has `#@ loop invariant count <= i`, you MUST also include `#@ loop invariant m >= 1`; without it the solver cannot prove `count <= i` is preserved when `m=0` allows `i` to stall on a match.
2. `kmp_build_failure` outer loop needs `#@ loop invariant k < m` (bounds for `pattern[k]`); do NOT include `#@ loop invariant k < i` — `k` can equal `i` after `k += 1` before `i += 1`, so this invariant is Unknown on preservation. The inner loop needs both `k < m` and `#@ loop invariant i < m` (so the solver can bound `k` after `k = failure[k-1]` using the fact that `pattern[i]` is still in-bounds).
3. `kmp_search` outer loop invariant must use `found <= n` (NOT `found <= n - m`): at initialisation `found = -1` so `found <= n - m` requires `n >= m - 1`, which no precondition establishes, causing a Timeout. Use `#@ loop invariant found <= n` and `#@ loop invariant i <= n` (text length), never `i <= m` (pattern length).
4. `kmp_search` inner loop (`while k > 0`) must also carry `#@ loop invariant i < n` so the solver can discharge the `text[i]` array-bounds check after the inner loop exits.
5. `kmp_search` postcondition is `#@ ensures True` — never write `1 == 1 - \length(pattern)`.
6. `kmp_search` is NOT self-recursive — omit any `#@ \variant` clause.

**Output (`count_occurrences`):**
```python
#@ requires \length(pattern) >= 1
#@ ensures \result >= 0
#@ assigns \nothing
def count_occurrences(text: list, pattern: list) -> int:
    count = 0
    n = len(text)
    m = len(pattern)
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant count >= 0
    #@ loop invariant count <= i
    #@ loop invariant m >= 1
    #@ loop variant n - i
    while i <= n - m:
        is_match = 1
        j = 0
        #@ loop invariant 0 <= j
        #@ loop invariant j <= m
        #@ loop variant m - j
        while j < m:
            if text[i + j] != pattern[j]:
                is_match = 0
            j += 1
        if is_match != 0:
            count += 1
            i += m
        else:
            i += 1
    return count
```

**Output (`kmp_build_failure`):**
```python
#@ requires True
#@ ensures True
#@ assigns \nothing
def kmp_build_failure(pattern: list) -> list:
    m = len(pattern)
    failure = [0] * m
    k = 0
    i = 1
    #@ loop invariant 1 <= i
    #@ loop invariant k >= 0
    #@ loop invariant k < m
    #@ loop invariant \length(failure) == m
    #@ loop variant m - i
    while i < m:
        #@ loop invariant k >= 0
        #@ loop invariant k < m
        #@ loop invariant i < m
        #@ loop variant k
        while k > 0 and pattern[k] != pattern[i]:
            k = failure[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        failure[i] = k
        i += 1
    return failure
```

**Output (`kmp_search`):**
```python
#@ requires True
#@ ensures \result >= -1
#@ ensures True
#@ assigns \nothing
def kmp_search(text: list, pattern: list) -> int:
    n = len(text)
    m = len(pattern)
    if m == 0:
        return 0
    failure = kmp_build_failure(pattern)
    k = 0
    i = 0
    found = -1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant k >= 0
    #@ loop invariant k < m
    #@ loop invariant found >= -1
    #@ loop invariant found <= n
    #@ loop variant n - i
    while i < n:
        #@ loop invariant k >= 0
        #@ loop invariant k < m
        #@ loop invariant i < n
        #@ loop variant k
        while k > 0 and pattern[k] != text[i]:
            k = failure[k - 1]
        if pattern[k] == text[i]:
            k += 1
        if k == m:
            found = i - m + 1
            i = n
        else:
            i += 1
    return found
```

---

## Example 12 — Mutex state machine (class invariant, no loops)

This pattern models a mutually-exclusive lock as a class with an integer
field `_active ∈ {0, 1}`. The class invariant is the sole proof anchor —
there are no loops, so no loop invariants are needed.

Key lessons:
- `beginning_execution` is a test-and-set: if idle (0), set to active (1)
  and return 1 (success); if already active, return 0 (failure).
- `ending_execution` requires `_active == 1` — this precondition is the
  proof obligation that prevents double-release.
- `can_execute` is a pure query (assigns nothing).

```python
""  # pycsl

#@ class invariant self._active == 0 or self._active == 1
class MutexGroup:
    def __init__(self) -> None:
        self._active: int = 0

    #@ ensures (\old(self._active) == 0) ==> (\result == 1 and self._active == 1)
    #@ ensures (\old(self._active) == 1) ==> (\result == 0 and self._active == 1)
    #@ assigns self._active
    def beginning_execution(self) -> int:
        was_idle = self._active
        self._active = 1
        if was_idle == 0:
            return 1
        return 0

    #@ requires self._active == 1
    #@ ensures self._active == 0
    #@ assigns self._active
    def ending_execution(self) -> None:
        self._active = 0

    #@ ensures (self._active == 0) ==> (\result == 1)
    #@ ensures (self._active == 1) ==> (\result == 0)
    #@ assigns \nothing
    def can_execute(self) -> int:
        if self._active == 0:
            return 1
        return 0
```

---

## Example 13 — Counter protocol (balanced enter/exit)

This pattern models a reference counter with class invariant `_count >= 0`.
The key insight is the precondition `_count >= 1` on the decrement method,
which is the proof obligation that prevents the counter from going negative.

```python
""  # pycsl

#@ class invariant self._count >= 0
class WorkTracker:
    def __init__(self) -> None:
        self._count: int = 0

    #@ ensures self._count == \old(self._count) + 1
    #@ assigns self._count
    def enter_work(self) -> None:
        self._count = self._count + 1

    #@ requires self._count >= 1
    #@ ensures self._count == \old(self._count) - 1
    #@ assigns self._count
    def exit_work(self) -> None:
        self._count = self._count - 1

    #@ ensures (\old(self._count) == 0) ==> (\result == 1)
    #@ ensures (\old(self._count) >= 1) ==> (\result == 0)
    #@ assigns \nothing
    def is_idle(self) -> int:
        if self._count == 0:
            return 1
        return 0
```

---

## Example 14 — Exceptional postconditions for validation

This pattern models a function that raises an exception on invalid input.
Note the workaround for TR-BUG-2: a local variable assignment is required
to prevent the transpiler from emitting the function as pure.

```python
_ = 0  # anchor

#@ requires depth >= 0
#@ requires history == 0 or history == 1
#@ ensures history == 0 ==> (\result[0] == 0 and \result[1] == depth)
#@ ensures (history == 1 and depth >= 1) ==> (\result[0] == 1 and \result[1] == depth)
#@ raises ValueError when history == 1 and depth == 0
#@ assigns \nothing
def qos_validate(history: int, depth: int) -> tuple:
    h = history    # local var forces mutable emission (TR-BUG-2 workaround)
    d = depth
    if h == 1 and d == 0:
        raise ValueError
    return (h, d)
```
