# Memory model extensions

Load when working in the `typed` or `store` memory models, or when
using `\valid`, `\separated`, `\at`, `\old(arr[i])`, label points,
ghost variables, or any of the typed-ghost types.

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

Worked example: `test-suite/corpus/pycsl-reference/0352.py` (compare with 0342.py which uses sequential local vars and doesn't need the snapshot). See [`transpiler-limits.md`](transpiler-limits.md) §4 for the full discussion.

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
