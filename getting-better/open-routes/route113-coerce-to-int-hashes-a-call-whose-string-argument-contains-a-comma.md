# ROUTE #113 — `_coerce_to_int` REPLACES A CALL WITH A HASH OF ITS TEXT when the call's
# lowered text merely CONTAINS A COMMA — and a comma inside a STRING-LITERAL ARGUMENT counts

**Status: FOUND, REPRODUCED, BOTH DIRECTIONS MEASURED (gen #23, 2026-09-14). NOT REPAIRED.**
**Severity: SEV-1. First-order.** A false postcondition is PROVED; the trigger is a comma in
an ordinary string argument (`g(y, "a,b")`).

## PROVENANCE

Generator `substring-census`. Gen #21's census listed it ("a COMMA in a string-literal
argument replaces the term with a text hash") and never ran it to a verdict. Gen #23 ran it.

## THE MECHANISM, quoted

`src/pycsl/module6_whyml/expressions.py`, the last arm of `_coerce_to_int`:

```
        # Tuple literals (a, b, c) → hash to int
        if "," in whyml_str and whyml_str.startswith("(") and whyml_str.endswith(")"):
            return str(stable_hash(whyml_str))
```

"Is this term a tuple?" is decided by a SUBSTRING TEST over generated text. A call lowers to
`(g !y "a,b")` — it starts with `(`, ends with `)`, and contains a comma inside the string
literal. It is classified as a tuple and **the whole call is replaced by the constant
`stable_hash("(g !y \"a,b\")")`**. The value, the callee's contract, and the dependence on
`y` are all discarded — and two calls with IDENTICAL TEXT over DIFFERENT VALUES get the SAME
constant.

## BOTH DIRECTIONS MEASURED at baseline worktree `21d5029e` (source == HEAD `6f36d67f`)

`c_comma2.py`:

```python
#@ ensures \result == x
#@ assigns \nothing
def g(x: int, s: str) -> int:
    return x

#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    y = x
    xs: List[int] = [g(y, "a,b")]
    a = xs[0]
    y = y + 1
    ys: List[int] = [g(y, "a,b")]
    b = ys[0]
    return b - a
```

- FALSE `\result == 0` — `[+] Verification SUCCESS` (rc=0). **CPython returns 1** (run).
  Emitted: `Array.make 1 (1542663842)` for BOTH literals.
- TRUE twin `\result == 1` — rc=1 (refused).
- CONTROL `c_nocomma2.py` — identical but the string is `"ab"`: emission keeps
  `(g !y "ab")`, the false claim is REFUSED on `f'vc` postcondition (read).

**The only difference between a false proof and an honest refutation is a comma inside a
string literal.** The first probe (`c_comma.py`, `g(x, ...)` vs `g(x + 1, ...)`) fired the
mechanism but the two TEXTS differed, so the hashes differed and the claim was refused — logged
as FAIL-CLOSED because the shape, not a fence, defeated it.

## REPAIR SKETCH (re-derive before landing)

Classify a tuple STRUCTURALLY: a comma at paren-depth 1 OUTSIDE string literals — or better,
from the IR node (`TupleLit`) rather than the text. A call is never a tuple and must pass
through (fail-closed: if it is not int-typed, Why3 rejects it). NOTE this alone does NOT close
route #114: a GENUINE tuple is still replaced by a hash of its TEXT.
