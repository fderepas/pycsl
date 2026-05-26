# Solver heuristics — loop invariant patterns

This file documents the loop-invariant patterns required to discharge proofs with Alt-Ergo within its step budget. These rules apply to invariant *content* — not syntax — and are specific to how Alt-Ergo and Z3 reason about linear arithmetic, induction, and array safety.

The common thread: Alt-Ergo prefers **explicit linear bounds** over implicit ones. When in doubt, state the bound directly rather than expecting the solver to derive it.

## Table of contents

1. [Binary search and two-pointer loops](#1-binary-search-and-two-pointer-loops)
2. [Sliding window and offset-start loops](#2-sliding-window-and-offset-start-loops)
3. [Conservation postconditions](#3-conservation-postconditions)
4. [Multiplicative accumulators](#4-multiplicative-accumulators)
5. [Binary flags and sentinels in nested loops](#5-binary-flags-and-sentinels-in-nested-loops)
6. [Avoiding vacuous contracts](#6-avoiding-vacuous-contracts)
7. [Nested-loop variable scope](#7-nested-loop-variable-scope)
8. [Type and English-comment rules](#8-type-and-english-comment-rules)

---

## 1. Binary search and two-pointer loops

When a loop uses two counters `left` and `right` with a loop guard `left <= right` and a variant `(right - left) + 1`, you **must** add both `#@ loop invariant left <= n` and `#@ loop invariant right < n` (where `n` is the pre-computed `len(...)` of the collection).

The one-sided lower-bound invariants `0 <= left` and `right >= -1` are too weak — Alt-Ergo cannot prove `(right - left + 1) >= 0` at loop entry from them alone, and exhausts its step budget. With `left <= n` and `right < n` (i.e. `right <= n - 1`) stated explicitly, the non-negativity goal `(right - left + 1) >= 0` is trivially provable from `right >= left` (loop guard) and `left <= n`, `right < n`.

Always include all four invariants as **separate** lines:

```
#@ loop invariant 0 <= left
#@ loop invariant left <= n
#@ loop invariant right >= -1
#@ loop invariant right < n
```

**CRITICAL: Do NOT write `#@ loop invariant 0 <= left and left <= right`.** The compound clause `left <= right` does NOT hold at loop entry when the array is empty (`n = 0`), because `right` is initialised to `n - 1 = -1` while `left = 0`, so `left <= right` is immediately false. The `left <= right` clause must never appear in any invariant.

---

## 2. Sliding window and offset-start loops

When a loop counter `i` is initialised to a **parameter** value (e.g., `i = k`) rather than to `0` or a computed constant, do NOT write `#@ loop invariant k <= i and i <= n`. The precondition can only guarantee `k >= 1`; it cannot guarantee `k <= n`, so Alt-Ergo cannot prove the lower-bound clause at loop entry.

Use the weaker but always-provable `#@ loop invariant 0 <= i` instead. At entry `i = k >= 1 > 0` satisfies `0 <= i`, and inside the loop the condition `i < n` keeps the variant `n - i` positive — so the solver can still discharge the postcondition without the upper-bound clause.

**This exception applies ONLY to parameter-initialized loops.** When `i` is initialised to a **literal constant** (e.g., `i = 1`), you MUST write the full two-sided bound:

```
#@ loop invariant 0 <= i and i <= n
```

Without the upper-bound clause `i <= n`, Alt-Ergo cannot prove the variant `n - i` non-negative at loop entry (the guard `i < n` is only available inside the loop body, not at entry). With `i <= n` stated explicitly, the variant non-negativity goal `(n - i) >= 0` is trivially provable from the invariant alone.

**Offset-access addition:** when the loop body contains an offset array access `values[i - k]`, you must also add a separate `#@ loop invariant k <= i` in addition to `#@ loop invariant 0 <= i`. This is required for Alt-Ergo to discharge the lower array-bounds obligation `i - k >= 0`. The invariant is always provable: at loop entry `i = k` so `k <= i` holds by reflexivity, and `i` is only ever incremented. Without it, Alt-Ergo cannot derive `i - k >= 0` from `0 <= i` alone, and times out on the safety VC.

Always write both `#@ loop invariant 0 <= i` and `#@ loop invariant k <= i` when offset accesses appear.

---

## 3. Conservation postconditions

When a function partitions or counts list elements into separate integer accumulators returned as a tuple, always add a `#@ ensures` that sums all accumulators to equal `n` (the pre-computed `len()` stored in a local variable before the loop).

**Use exact equality in the matching loop invariant** — `#@ loop invariant acc1 + acc2 + ... == i` (not `<= n`). When the loop exits `i == n`, so the conservation postcondition is immediately provable. A `<= n` invariant is too weak and will cause Alt-Ergo to fail on the postcondition even though the code is correct.

See Example 4 (`count_categories`) in `SKILL.md` for the canonical pattern.

---

## 4. Multiplicative accumulators

When a function uses a **multiplicative accumulator** (e.g., `acc *= k`):

- Name the accumulator `acc`, never `result` (see the reserved-keyword rule in `transpiler-limits.md`).
- Add the individual sign invariants `#@ loop invariant acc >= 1` and `#@ loop invariant k >= 0`.
- **Do NOT add** a cross-product invariant of the form `#@ loop invariant acc * k >= 1`. This is a nonlinear arithmetic expression that Alt-Ergo cannot verify and will produce 'Unknown'.

The `acc >= 1` invariant alone is sufficient: inside the loop `!k >= 2` (from `!k > 1`), so `acc * k >= 1 * 2 >= 1` is maintained without stating it explicitly. When the loop exits `!k = 1`, so `!acc >= 1` directly closes the postcondition `\result >= 1`.

**Always use `#@ requires n >= 1`** (not `n >= 0`) for such functions. See Example 7 (`factorial`) in `SKILL.md`.

---

## 5. Binary flags and sentinels in nested loops

When a function uses a binary flag variable (e.g., `found = 0` set to `1` when a match is detected) together with a sentinel result variable (e.g., `found_val = -1` set to the matched value on success), you must bound both variables from both sides in every loop that touches them.

**Outer loop:**
```
#@ loop invariant 0 <= i and i <= n
#@ loop invariant found >= 0
#@ loop invariant found <= 1
#@ loop invariant found_val >= -1
#@ loop variant n - i
```

**Inner loop** (any inner loop that may update these variables):
```
#@ loop invariant 0 <= j and j <= i
#@ loop invariant found >= 0
#@ loop invariant found <= 1
#@ loop invariant found_val >= -1
#@ loop variant i - j
```

Without these explicit bounds, Alt-Ergo exhausts its step budget trying to infer the ranges from the loop structure alone and reports 'Unknown' on variant and invariant proof obligations. Specifically:

- `found <= 1` — upper bound (`found` is only ever 0 or 1).
- `found_val >= -1` — lower bound (the sentinel is `-1` before any match).
- `found >= 0` (inner loop) — lower bound (`found` is initialised to 0 and never decremented).

---

## 6. Avoiding vacuous contracts

**NEVER write `#@ requires True` or `#@ ensures True` when a meaningful, provable contract exists.** Reserve them only for genuinely empty preconditions or unprovable postconditions:

- `#@ requires True` — a function that accepts any integer without restriction.
- `#@ ensures True` — when the return value genuinely has no useful property the solver can verify.

For a multiplicative accumulator (e.g., `factorial`), write `#@ requires n >= 1` (not `n >= 0` — see §4) and `#@ ensures \result >= 1`.

For additive accumulators over **list** parameters (e.g., `sum_list`), **always use `#@ ensures True`** because list elements may be negative, making `\result >= 0` unprovable for arbitrary inputs. Do NOT add `#@ loop invariant total >= 0` or `#@ loop invariant acc >= 0` when iterating over a list parameter, for the same reason. See Example 8 (`sum_list`) in `SKILL.md`.

**Exception — counting accumulators.** When a variable named `count` is only ever incremented (never decremented) inside the loop body (e.g., `count += 1` guarded by a positivity check), it is always `>= 0`. You MUST add `#@ loop invariant count >= 0` — it is both provable and required to close a `#@ ensures \result >= 0` postcondition.

**Exception — positive-only accumulation.** When the loop body uses `continue` to skip non-positive elements before accumulating (e.g., `if values[i] <= 0: i += 1; continue`), the accumulator only ever receives positive increments and is always `>= 0`. You MUST add `#@ loop invariant total >= 0` (and `#@ ensures \result >= 0`) — both are provable and required to verify the postcondition. See Example 5 (`running_total_until`) in `SKILL.md`.

---

## 7. Nested-loop variable scope

A `while` loop nested inside a `for` loop does NOT have the `for`-loop iteration variable in scope for its invariants. Only reference variables that are actually assigned **before** the `while` keyword (e.g., local variables, function parameters, and variables set in the enclosing function body).

For example, if `for i in range(n)` contains a `while j >= 0` loop, write `#@ loop invariant -1 <= j and j < n` — NOT `#@ loop invariant -1 <= j and j < i`, because `i` is the `for`-loop control variable and is not a stable, in-scope binding for the nested `while` invariant.

**Exception — `while`-inside-`while` with a go-flag pattern.** When an inner `while go == 1` loop is nested inside an outer `while i < n` loop (as in `insertion_sort`-style algorithms), `i` IS a regular mutable variable that is in scope and does NOT change inside the inner loop body. In this case you MUST add both:

```
#@ loop invariant j < i
#@ loop invariant i < n
```

Together these give `j < i < n`, which lets Alt-Ergo prove `values[j]` is a valid array access, and `j + 1 <= i < n` which proves `values[j+1]` is also valid — both without nonlinear arithmetic. Without these two invariants Alt-Ergo cannot bound `j` from above and will time out on the array-access safety obligations.

---

## 8. Type and English-comment rules

**Type Limits:** Assume integers are unbounded mathematical integers. Do not write contracts that depend on machine-integer overflow.

**No English:** Never write English explanations on the same line as a `#@` contract. Anything after the contract expression on the same line will be parsed as part of the expression and produce a syntax error.
