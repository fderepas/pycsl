# Route #203 — a single-part f-string was the integer it interpolates

**Status:** CLOSED (gen #30). SEV-1. Decisive signature present, and the defect is a wrong
**decision**, not a merely-unknown value.

## The witness

```python
#@ ensures \result == 2
def probe() -> int:
    n = 5
    s = f"{n}"
    if s == "5":
        return 1
    return 2
```

Emitted:

```whyml
let s = ref 0 in
let n = ref 0 in
n := 5;
s := !n;                      (* the f-string IS the integer *)
if (!s = 1359629258) then ... (* 1359629258 = stable_hash('"5"') *)
```

`\result == 2` PROVED. CPython answers **1**, because `f"{5}"` IS `"5"`. The TRUE twin
`\result == 1` was REFUSED.

Corpus: `1705_route203_an_int_interpolated_fstring_was_the_integer.py` (expected FAIL),
`1706_route203_two_equal_ints_give_equal_fstrings.py` (completeness control, PASSES).

## Where it came from

Question 2 of the backlog's three — *which other arm of the same function reaches the same
answer?* — applied to route #199's own function, `_handle_fstring_expr`. #199 repaired the
EMPTY-parts arm. This is the INT-MODEL joiner underneath it.

## Why the arm is narrow, which is what made the repair landable

```python
acc = _part(parts[0])
for part in parts[1:]:
    self._add_abstract_op("val str_concat (x: int) (y: int) : int")
    acc = f"(str_concat {acc} {p})"
return acc
```

* a MULTI-part f-string is wrapped in `str_concat`, an abstract op with no axioms — opaque;
* a STRING-typed part goes through `str_hash_op` — opaque;
* **a SINGLE-part f-string whose part is not string-typed returns `acc` exactly as `_part`
  produced it** — the raw value.

Static census of that exact shape (`JoinedStr` with one value, a `FormattedValue`):

| tree | files | single-part f-strings |
|---|---|---|
| `test-suite/corpus/pycsl-reference` | 1630 | **0** |
| `src/self-annotate/src` | 53 | **0** |
| `src/pycsl_lib` | 104 | **0** |
| live `src/pycsl` | 94 | 3, none of them in a mirrored function |

575 f-strings in the mirror was the *upper bound*; the arm that is actually wrong is empty.
Scoping the repair to `len(parts) == 1` is what keeps it from touching the other 575.

## The repair, and why it could be a DECLARED opaque

```python
if len(parts) == 1 and not acc.strip().startswith("(str_hash_op "):
    self._add_abstract_op("val function str_of_int_hash (x: int) : int")
    acc = f"(str_of_int_hash {acc})"
```

Routes #193/#194/#195/#201 were forced to the declaration-free `(any …)` because their
methods' mirrors are CONVERTED with `assigns \nothing`, and `_add_abstract_op` would make
them effectful. `_handle_fstring_expr`'s mirror is a **re-trusted stub**, so that constraint
does not apply here — worth checking each time rather than assuming the harder answer.

A *value-keyed* opaque is strictly better than `any` here, and witness `1706` is what pins
it: `str_of_int_hash` is deterministic, so `f"{n}" == f"{n}"` still PROVES, which is what
Python says. A later "simplification" to `(any int)` would still pass `1705` and silently
lose `1706`.

## Prediction vs measurement

| | predicted | measured |
|---|---|---|
| `\result == 2` (false) | REFUSED | REFUSED |
| `\result == 1` (true twin) | REFUSED (opaque answers neither) | REFUSED |
| two equal `n`s give equal strings | PROVES | PROVES (1706) |
| corpus + mirror byte-diff | ZERO (0 occurrences of the shape in either) | see the battery record |
