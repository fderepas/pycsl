# Matrix and 2D-array patterns

This file covers verification of algorithms involving matrices, 2D lists, stride-based pointer arithmetic, and any code that produces nonlinear verification conditions (VCs). It documents two complementary approaches — **flat 1D rewrite** (§1–§3) and **native 2D arrays** (§4) — plus cautionary worked examples (§5) and a table of provable linear patterns (§6).

**Decision tree for matrix-style programs:**

```
Encounter a matrix-style program
        │
        ▼
Does the original Python use 2D lists (matrix[i][j])?
        │
    YES │                           NO │
        ▼                              ▼
Use native 2D array support     Proceed with flat-loop
via \length2d / \valid2d        annotation using a single
(§4 below). Nested for loops    index variable and n parameter.
with range(m)/range(n) map      Use Examples 1–8 from SKILL.md
directly to matrix.Matrix.      as templates.
```

---

## §1 — The nonlinear-arithmetic problem

When a Python program uses 2D nested lists (`matrix[i][j]`) or stride-based pointer loops (`ptr += stride` where `stride` is a symbolic variable), converting them to flat 1D array accesses inevitably introduces **nonlinear arithmetic** in the VCs:

- `i * cols + j < rows * cols` — bounds for `matrix[i * cols + j]`
- `dst + rows < rows * cols` — bounds for `out[dst]` after `dst += rows`
- `j + k * b_cols < a_cols * b_cols` — bounds for `b[j + k * b_cols]`

**Neither Alt-Ergo nor Z3 can discharge these goals reliably.** Alt-Ergo has no nonlinear arithmetic. Z3's NIA (nonlinear integer arithmetic) times out or runs out of memory on complex nested-loop queries even after `split_vc` decomposes them.

**Signs you are hitting this problem:**

- Why3 reports `Timeout (30.00s, NNM steps)` with N > 20 million steps, or `Out of memory`.
- `split_vc` passes all simple sub-goals but specific *preservation* or *bounds* sub-goals time out.
- The failing sub-goals involve `dst < n`, `b_ptr < n_b`, `ptr + stride < total`, or any "pointer stays in bounds" obligation where `stride` is a loop variable.

---

## §2 — The fix: linear-access rewrite

When the original Python algorithm uses 2D lists or stride-based pointer arithmetic, **replace it with a linear-access algorithm** that:

1. Uses a single loop variable `i` as the **direct** array index (`arr[i]`).
2. **Never** computes array indices as `expr1 * expr2` where both `expr1` and `expr2` are symbolic variables.
3. Has no product of two symbolic variables anywhere in its loop invariants.

**Key principle:** The invariant `0 <= i and i <= n` plus the loop guard `i < n` proves `arr[i]` is in bounds using only the precondition `\length(arr) >= n` — purely linear, Alt-Ergo discharges it in under 10,000 steps.

### Linear-access pattern table

| Original pattern | Why it fails | Linear replacement |
|---|---|---|
| `matrix[i][j]` — 2D nested list | Flat index `i * cols + j < rows * cols` is nonlinear | Flat array `arr[pos]` with `pos` a single monotone counter |
| `out[j * rows + i] = v` | `j * rows` product of two variables | `out[i] = v` with `i` the primary counter |
| `b_ptr += b_cols` (symbolic stride) | `b_ptr < n_b` preservation requires `k * b_cols < n_b` | Element-wise parallel iteration: `a[i]` and `b[i]` together |
| Nested loops over `rows × cols` | Cross-loop bounds need `i * cols + j < rows * cols` | Single flat loop over `n = rows * cols` elements |

### What NOT to add as a loop invariant

| ❌ Do NOT add | Reason |
|---|---|
| `a_row_start + a_cols <= n_a` (outer loop) | **False** at the last iteration: after `a_row_start += a_cols`, equals `n_a`; then `n_a + a_cols > n_a` — unprovable |
| `out_row_start + b_cols <= n_out` (outer loop) | Same: **false** at the last iteration |
| `dst < n` when `dst += rows` in a branch | Preservation needs `dst + rows < rows * cols` — nonlinear; Z3 NIA times out |
| `b_ptr < n_b` in a k-loop with `b_ptr += b_cols` | Preservation after last body step requires `j + a_cols * b_cols < n_b` — nonlinear |
| `b_ptr == j + k * b_cols` | Product `k * b_cols` — Alt-Ergo returns Unknown |
| `i * cols + j == src` | Product `i * cols` — nonlinear; Alt-Ergo returns Unknown |

---

## §3 — Explicit-`n` parameter strategy

When you must verify a matrix algorithm and cannot use native 2D arrays (§4), restructure as a single flat `while` loop with an explicit `n` integer parameter that the caller pre-computes.

### Preconditions

```
#@ requires n >= 1
#@ requires \length(matrix) >= n
#@ requires \length(out) >= n
#@ requires n == rows * cols
```

The last clause is critical — it lets Why3 substitute `n` for `rows*cols` and reduce nonlinear products to linear bounds. Without it, you cannot derive useful linear facts from the matrix dimensions.

For matrix-multiply, also add the linear preconditions Alt-Ergo cannot derive on its own:

```
#@ requires a_rows <= n_out
#@ requires b_cols <= n_out
#@ requires a_cols <= n_a
#@ requires a_cols <= n_b
#@ requires b_cols <= n_b
```

For `transpose`, add `#@ requires rows <= n` (follows from `n == rows * cols` and `cols >= 1`).

### Single flat while loop

Replace nested `while i < rows` / `while j < cols` (or `while k < a_cols`) with a single `while src < n:` loop (incrementing `src` by `1` each iteration), tracking secondary indices or accumulators explicitly in the body.

### Linear invariants

```
#@ loop invariant 0 <= src and src <= n
```

Array-access safety for `matrix[src]` follows directly from the loop guard `src < n` plus the precondition `\length(matrix) >= n` — no separate strict upper-bound invariant is needed for `src`.

For the secondary `dst` accumulator in `transpose`, always add `#@ loop invariant dst < n` (strict upper bound, sufficient for array safety since the algorithm visits each output index exactly once). Do NOT add `#@ loop invariant dst + rows <= n` — this is mathematically invalid: at the start of last-column iterations for row index `i >= 1`, `dst + rows` exceeds `n` (e.g., a 2×2 matrix at the start of the last iteration: `dst=3`, `rows=2`, `n=4` → `3+2=5>4`).

Do NOT add `#@ loop invariant dst <= src` — not a true invariant: after `dst += rows` and `src += 1`, `dst` exceeds `src` whenever `rows > 1`.

### Replace the `j` counter with a `cols_left` countdown

Use a `cols_left` countdown variable instead of an upward-counting `j`:

- Initialise `cols_left = cols` before the loop.
- Decrement `cols_left -= 1` each iteration.
- When `cols_left > 0`, advance `dst += rows`; otherwise reset `cols_left = cols`, advance `i += 1`, and **guard `dst = i` with `if i < rows:`** — this prevents `dst` from reaching `n` when `i` has just been incremented to `rows` on the last iteration.

Add `#@ loop invariant 0 < cols_left and cols_left <= cols` (purely linear) instead of `#@ loop invariant j < cols`.

Also keep `#@ loop invariant i >= 0`, `#@ loop invariant i <= rows`, and `#@ loop invariant rows <= n`. Always add `#@ loop invariant i <= src` — this structural bound gives Alt-Ergo a linear relationship between `i` and `src`, useful for bounding the else-branch where `dst := i`.

### Matrix-multiply outer-loop invariants

```
#@ loop invariant a_row_start <= n_a
#@ loop invariant out_row_start <= n_out
#@ loop invariant out_row_start + b_cols <= n_out
```

Use `<=` throughout — strict `<` is violated at the last iteration. The `out_row_start + b_cols <= n_out` invariant is required to discharge array safety inside the `j`-loop body.

### Matrix-multiply `j`-loop invariants

```
#@ loop invariant out_row_start + j <= n_out
```

Use `<=` (not strict `<`) because after incrementing `j` to `b_cols` on the last iteration `out_row_start + b_cols = n_out`. Array-access safety for `out[out_row_start + j]` inside the body is guaranteed by the loop guard `j < b_cols` combined with this invariant.

### Matrix-multiply inner `k`-loop invariants

```
#@ loop invariant a_ptr < n_a
#@ loop invariant a_ptr <= n_a
#@ loop invariant a_ptr == a_row_start + k
```

The non-strict bound (`a_ptr <= n_a`) gives Alt-Ergo a direct linear bound without combining the pointer equality with outer-loop invariants. The linear equality `a_ptr == a_row_start + k` is inductive and lets Alt-Ergo verify `a_ptr < n_a` at each access.

For `b_ptr`, **do NOT add** `b_ptr < n_b` — after `b_ptr += b_cols` on the last body step (`k = a_cols-1`), `b_ptr = j + n_b >= n_b`, violating the strict bound. **Do NOT add** `b_ptr == j + k * b_cols` — the product `k * b_cols` is nonlinear. Instead add only the purely additive bound:

```
#@ loop invariant b_ptr >= j
```

Since `b_ptr` starts at `j` and only increases, combined with the loop guard and the outer j-loop invariant `out_row_start + j <= n_out`, this gives Alt-Ergo sufficient linear context for array-access safety on `b[b_ptr]`.

---

## §4 — Native 2D arrays with `\length2d` and `\valid2d`

PyCSL supports 2D arrays natively using Why3's `matrix.Matrix` module. This eliminates all nonlinear arithmetic — **do NOT rewrite 2D code as flat 1D arrays when this support is available.**

### Key predicates

| PyCSL syntax | WhyML expansion | Meaning |
|---|---|---|
| `\length2d(a, m, n)` | `a.rows = m && a.columns = n` | `a` is an `m × n` matrix |
| `\valid2d(a, i, j)` | `valid_index a i j` | `(i,j)` is a valid index (linear check) |

### Why it works

`valid_index a r c` expands to `0 <= r < a.rows /\ 0 <= c < a.columns` — **purely linear** bounds. No multiplication. Alt-Ergo and Z3 discharge these instantly.

### Parameter typing

Any parameter used as `a[i][j]` (or declared via `\length2d`) becomes `matrix int` in WhyML automatically. No type hint is needed in Python — the transpiler detects 2D usage.

### Required file header

Every 2D-annotated file must start with:

```python
""  # pycsl
```

This ensures the `#@ requires` comments attach correctly to the function.

### `for` loop annotation placement

Loop invariants and variants for `for i in range(m):` must be placed immediately before the `for` line as `#@` comments:

```python
#@ loop invariant 0 <= i and i <= m
#@ loop variant m - i
for i in range(m):
```

Inside the invariant, `i` refers to the loop counter as an integer.

### Template — nested for loop over 2D array

```python
""  # pycsl
#@ requires \length2d(a, m, n)
#@ requires m >= 0
#@ requires n >= 0
def my_2d_function(a, m, n, ...):
    #@ loop invariant 0 <= i and i <= m
    #@ loop variant m - i
    for i in range(m):
        #@ loop invariant 0 <= j and j <= n
        #@ loop variant n - j
        for j in range(n):
            ... a[i][j] ...
```

### Mixed 1D + 2D arrays

If a function takes both a 2D input and a 1D output, use `\length2d` for the matrix and `\valid` for the 1D array:

```python
""  # pycsl
#@ requires \length2d(a, m, n)
#@ requires \valid(sums, m)
#@ requires m >= 0
#@ requires n >= 0
def matrix_row_sum(a, sums, m, n):
    #@ loop invariant 0 <= i and i <= m
    #@ loop variant m - i
    for i in range(m):
        s = 0
        #@ loop invariant 0 <= j and j <= n
        #@ loop variant n - j
        for j in range(n):
            s = s + a[i][j]
        sums[i] = s
```

### Multiple 2D arrays

Each 2D array needs its own `\length2d`:

```python
""  # pycsl
#@ requires \length2d(a, m, n)
#@ requires \length2d(b, m, n)
#@ requires \length2d(c, m, n)
#@ requires m >= 0
#@ requires n >= 0
def matrix_add(a, b, c, m, n):
    #@ loop invariant 0 <= i and i <= m
    #@ loop variant m - i
    for i in range(m):
        #@ loop invariant 0 <= j and j <= n
        #@ loop variant n - j
        for j in range(n):
            c[i][j] = a[i][j] + b[i][j]
```

### Square matrices

For operations on the diagonal or any square matrix, use `\length2d(a, n, n)`:

```python
""  # pycsl
#@ requires \length2d(a, n, n)
#@ requires n >= 0
def matrix_zero_diagonal(a, n):
    result = 1
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    for i in range(n):
        if a[i][i] != 0:
            result = 0
    return result
```

### What NOT to do for 2D arrays

- **Do NOT** rewrite `a[i][j]` as `a[i*cols + j]` — that creates nonlinear VCs.
- **Do NOT** use `array (array int)` — Why3 forbids mutable nested arrays.
- **Do NOT** omit `\length2d` — without it the transpiler cannot type the parameter.

---

## §5 — Cautionary examples

The two examples below illustrate algorithms where the flat-rewrite strategy (§3) can be *attempted* but several invariants remain unprovable with current SMT solvers. **Prefer the native 2D approach (§4) or the linear patterns (§6) whenever possible.**

### Cautionary Example A — Matrix transpose

> ⚠️ **ASPIRATIONAL ONLY.** The annotations shown below are what the agent should AIM FOR, but several invariants remain **unprovable** with current SMT solvers. Specifically, the preservation of `#@ loop invariant dst < n` in the `cols_left > 0` branch (where `dst += rows`) requires proving `dst + rows < rows * cols` — a product of two symbolic variables. Both Alt-Ergo and Z3 NIA time out on this sub-goal even with `split_vc`. If you encounter a `transpose`-style algorithm with conditional pointer arithmetic, **prefer the native 2D rewrite in §4 instead.**

**Input:**
```python
def transpose(matrix: list, rows: int, cols: int, out: list) -> int:
    i = 0
    while i < rows:
        j = 0
        while j < cols:
            src = i * cols + j
            dst = j * rows + i
            out[dst] = matrix[src]
            j += 1
        i += 1
    return 0
```

**Output (aspirational):**
```python
#@ requires rows >= 1
#@ requires cols >= 1
#@ requires n >= 1
#@ requires n == rows * cols
#@ requires rows <= n
#@ requires \length(matrix) >= n
#@ requires \length(out) >= n
#@ ensures \result == 0
#@ assigns \nothing
def transpose(matrix: list, rows: int, cols: int, n: int, out: list) -> int:
    src = 0
    i = 0
    cols_left = cols
    dst = 0
    #@ loop invariant 0 <= src and src <= n
    #@ loop invariant dst >= 0
    #@ loop invariant dst < n
    #@ loop invariant i >= 0
    #@ loop invariant i <= rows
    #@ loop invariant i <= src
    #@ loop invariant rows <= n
    #@ loop invariant 0 < cols_left and cols_left <= cols
    #@ loop variant n - src
    while src < n:
        out[dst] = matrix[src]
        src += 1
        cols_left -= 1
        if cols_left > 0:
            dst += rows
        else:
            i += 1
            cols_left = cols
            if i < rows:
                dst = i
    return 0
```

### Cautionary Example B — Matrix multiply

> ⚠️ **CONTAINS FALSE INVARIANTS.** The annotations shown below include two loop invariants that are **mathematically false** at the last loop iteration and **must not be used**:
> - `#@ loop invariant a_row_start + a_cols <= n_a` — **false** when `i = a_rows - 1`: after the final `a_row_start += a_cols`, `a_row_start` equals `n_a`, making `n_a + a_cols > n_a`.
> - `#@ loop invariant out_row_start + b_cols <= n_out` — same issue.
> - `#@ loop invariant out_idx < n_out` in the j-loop — `out_idx` holds its stale value from the previous j-iteration at loop entry; proving this requires the false outer invariant above.
>
> These invariants cause Why3 to time out (100–170 million steps) trying to prove statements that are unprovable. Additionally, `b_ptr < n_b` in the k-loop and `dst < n` preservation both require nonlinear reasoning that Z3 NIA cannot discharge within 30 seconds. **Use the native 2D approach (§4) or the linear patterns (§6) instead** whenever the original Python uses 2D lists or stride-based pointer arithmetic.

**Input:**
```python
def multiply(a: list, b: list, a_rows: int, a_cols: int, b_cols: int, n_a: int, n_b: int, n_out: int, out: list) -> int:
    i = 0
    a_row_start = 0
    out_row_start = 0
    while i < a_rows:
        j = 0
        while j < b_cols:
            cell = 0
            k = 0
            a_ptr = a_row_start
            b_ptr = j
            while k < a_cols:
                cell += a[a_ptr] * b[b_ptr]
                a_ptr += 1
                b_ptr += b_cols
                k += 1
            out_idx = out_row_start + j
            out[out_idx] = cell
            j += 1
        a_row_start += a_cols
        out_row_start += b_cols
        i += 1
    return 0
```

**Output (aspirational — see warning above):**
```python
#@ requires a_rows >= 1
#@ requires a_cols >= 1
#@ requires b_cols >= 1
#@ requires n_a >= 1
#@ requires n_b >= 1
#@ requires n_out >= 1
#@ requires n_a == a_rows * a_cols
#@ requires n_b == a_cols * b_cols
#@ requires n_out == a_rows * b_cols
#@ requires a_rows <= n_out
#@ requires b_cols <= n_out
#@ requires a_cols <= n_a
#@ requires a_cols <= n_b
#@ requires b_cols <= n_b
#@ requires \length(a) >= n_a
#@ requires \length(b) >= n_b
#@ requires \length(out) >= n_out
#@ ensures \result == 0
#@ assigns \nothing
def multiply(a: list, b: list, a_rows: int, a_cols: int, b_cols: int, n_a: int, n_b: int, n_out: int, out: list) -> int:
    i = 0
    a_row_start = 0
    out_row_start = 0
    out_idx = 0
    #@ loop invariant 0 <= i and i <= a_rows
    #@ loop invariant a_row_start >= 0
    #@ loop invariant a_row_start <= n_a
    #@ loop invariant a_row_start + a_cols <= n_a
    #@ loop invariant out_row_start >= 0
    #@ loop invariant out_row_start <= n_out
    #@ loop invariant out_row_start + b_cols <= n_out
    #@ loop variant a_rows - i
    while i < a_rows:
        j = 0
        #@ loop invariant 0 <= j and j <= b_cols
        #@ loop invariant out_row_start + j <= n_out
        #@ loop invariant out_idx < n_out
        #@ loop variant b_cols - j
        while j < b_cols:
            cell = 0
            k = 0
            a_ptr = a_row_start
            b_ptr = j
            out_idx = out_row_start + j
            #@ loop invariant 0 <= k and k <= a_cols
            #@ loop invariant a_ptr >= 0
            #@ loop invariant a_ptr < n_a
            #@ loop invariant a_ptr <= n_a
            #@ loop invariant a_ptr == a_row_start + k
            #@ loop invariant b_ptr >= 0
            #@ loop invariant b_ptr >= j
            #@ loop variant a_cols - k
            while k < a_cols:
                cell += a[a_ptr] * b[b_ptr]
                a_ptr += 1
                b_ptr += b_cols
                k += 1
            out[out_idx] = cell
            j += 1
        a_row_start += a_cols
        out_row_start += b_cols
        i += 1
    return 0
```

---

## §6 — Five provable linear flat-matrix operations

These five patterns cover the most common matrix-shaped computations. All are **fully provable with Alt-Ergo alone** (no Z3 needed, sub-millisecond per sub-goal). Use them as templates whenever the algorithm can be expressed without stride-based pointer arithmetic.

```python
""  # pycsl
#@ requires n >= 0
#@ requires \length(out) >= n
#@ ensures \result == 0
#@ assigns \nothing
def matrix_fill(out: list, n: int, value: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        out[i] = value
        i += 1
    return 0


#@ requires n >= 0
#@ requires \length(a) >= n
#@ requires \length(b) >= n
#@ requires \length(out) >= n
#@ ensures \result == 0
#@ assigns \nothing
def matrix_add(a: list, b: list, out: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        out[i] = a[i] + b[i]
        i += 1
    return 0


#@ requires n >= 0
#@ requires \length(a) >= n
#@ requires \length(out) >= n
#@ ensures \result == 0
#@ assigns \nothing
def matrix_scale(a: list, out: list, n: int, factor: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        out[i] = a[i] * factor
        i += 1
    return 0


#@ requires n >= 1
#@ requires \length(a) >= n
#@ assigns \nothing
def matrix_max(a: list, n: int) -> int:
    best = a[0]
    i = 1
    #@ loop invariant 1 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if a[i] > best:
            best = a[i]
        i += 1
    return best


#@ requires n >= 0
#@ requires \length(src) >= n
#@ requires \length(dst) >= n
#@ ensures \result == 0
#@ assigns \nothing
def matrix_copy(src: list, dst: list, n: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        dst[i] = src[i]
        i += 1
    return 0
```

**Why these work:**

- Every array access is `arr[i]` — the bounds proof is `i < n` (loop guard) + `\length(arr) >= n` (precondition) — purely linear.
- `0 <= i and i <= n` has a trivial init and a trivial preservation proof.
- No strides, no products of variables, no conditional pointer updates.
