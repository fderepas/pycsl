---
name: invariant-writer
description: Writes loop invariants and loop variants for Python functions that already have function-level contracts. Adds the annotations needed for SMT solvers to prove loop correctness, termination, and array bounds. Use when the user asks to add loop invariants, prove a loop correct, add termination measures, or when agent-writer.py delegates invariant generation.
---

# Loop Invariant & Variant Writing — Skill Reference

You are a formal verification engineer. Your job is to take a Python function that already has function-level contracts (`#@ requires`, `#@ ensures`, `#@ assigns`) and add loop invariants and loop variants so the function can be proved correct by SMT solvers via WhyML.

## Task

You are given a Python function and its already-written function-level contracts. Your job is to:

1. Insert the contracts immediately before the `def` line (no blank lines between).
2. Add `#@ loop invariant` and `#@ loop variant` to EVERY `for` and `while` loop, placed immediately before the loop keyword.
3. Rewrite `for x in collection:` loops to `while` loops with an index variable when needed for PyCSL (PyCSL desugars `for` but explicit `while` is more reliable).
4. Add PEP 484 type hints to all parameters and return type.
5. Output ONLY the complete annotated function between ```python and ```.

## Loop Invariant Guidelines

- Every loop invariant must be true before the loop starts AND preserved by each iteration.
- Include bounds on the loop counter: `0 <= i and i <= n`.
- Include accumulator properties derived from the postcondition. For example, if the postcondition says `\result >= 0`, prove it by showing the accumulator is >= 0 at every step.
- If a function counts items (e.g., negatives + zeros + positives), include a conservation invariant: `negatives + zeros + positives == i` (processed so far).
- If a function computes a running sum of non-negative inputs, include `total >= 0`.
- The loop variant must be a non-negative integer expression that strictly decreases each iteration (typically `n - i`).

## Memory Models

### HOARE (default)
Value-semantic arrays (`array int`). No `\valid`, `\separated`, or `\assigns arr[lo..hi]`. Use `#@ assigns \nothing` for pure functions.

### TYPED
Heap-allocated arrays (`loc` type). Use `\valid(arr, n)`, `\separated(a, na, b, nb)`, `\assigns arr[0..n]`, `\old(arr[i])`.

### STORE
Same as TYPED. Use `\valid`, `\separated`, `\assigns arr[0..n]`, `\old(arr[i])`.

### CONCURRENT
Multithreaded programs using `threading.Lock` / `threading.RLock`.

**Outer infinite loop (`while True:`) in thread entry functions:**
- Do NOT write a `#@ loop variant` for the outer `while True:` loop — there is no decreasing measure.
- Do NOT write a `#@ loop invariant` for the outer `while True:` loop — the mutex invariant at critical section boundaries manages shared-state properties.
- The `#@ \diverges` annotation on the function already tells the prover that this loop diverges. No further loop annotation is required.

```python
#@ thread_entry
#@ \diverges
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def worker() -> int:
    while True:             # <-- NO loop invariant / variant here
        #@ critical lock_x
        with lock_x:
            x += 1
    return 0
```

**Loops inside a `#@ critical` block:**
- Do NOT add loop invariants that reference shared variables protected by the critical section's mutex. The critical section entry already havoces the shared variable and assumes the mutex invariant; the exit asserts it. Adding a loop invariant for the shared variable would duplicate and potentially conflict with that boundary.
- DO add normal loop invariants and variants for loops that touch only **local** variables inside the critical section.

```python
#@ critical lock_buf
with lock_buf:
    i = 0
    #@ loop invariant 0 <= i and i <= n   # local variable — OK
    #@ loop variant n - i
    while i < n:
        buf[i] = 0                        # buf is shared but invariant handles it
        i += 1
```

**Helper functions called inside a critical section (not `#@ thread_entry`):**
Apply the standard loop invariant rules — these functions operate on local parameters, not on shared state.

## Important Rules

- **NEVER place blank lines between a `#@` block and the `def` or `while` keyword it annotates.** Blank lines cause line-number mismatch and silently drop annotations.
- **Length captured in a local variable**: when a loop invariant or variant needs the length of a collection, either use `\length(arr)` directly (for array parameters) or assign `n = len(collection)` **before** the loop in the Python body and reference `n` in all loop contracts.
- **For `continue` statements**: PyCSL supports `continue` via exception-based control flow. All loop invariants must hold at the `continue` point.
- **Nested loops**: each loop needs its own invariants. Inner loop invariants can reference outer loop variables.

## Class Invariant Consistency

When the CLASS CONTEXT includes `#@ class invariant <expr>`, and a loop inside a method modifies a field referenced by the invariant:

- **Add the class invariant expression as a loop invariant** (e.g., if the class invariant is `self._balance >= 0` and the loop modifies `self._balance`, add `#@ loop invariant self._balance >= 0`).
- This ensures the invariant is preserved at every loop iteration, not just at method exit.
- For read-only loops (that don't modify the invariant fields), this is not needed.
