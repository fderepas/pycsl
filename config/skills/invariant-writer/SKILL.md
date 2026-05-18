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
