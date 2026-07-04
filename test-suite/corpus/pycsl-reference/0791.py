"""Test 0791 — .lower()/.upper() are content-faithful (idempotent + literal-folded).

cleared-string RESIDUALS item 1. `.lower()`/`.upper()` now lower to DETERMINISTIC
`val function str_lower_op`/`str_upper_op` (not a fresh-per-call `val`), carrying the
UNIVERSAL sound content law IDEMPOTENCE (Python str.lower/upper are idempotent for
ALL strings, Unicode included) — encoded via a fresh "already-folded" marker
predicate, no new `axiom`. So:
  * `lower_idempotent` — `s.lower().lower() == s.lower()` PROVES (was Unknown under
    the old non-deterministic length-only `str_case_op`); expressed in the body
    (`.lower()` is rejected in a contract by design);
  * `fold_upper_literal` — a STRING-LITERAL receiver is CONSTANT-FOLDED by Python's
    own `str.upper()`, so `"Hello World".upper() == "HELLO WORLD"` is exact content.
`s.lower() == s.upper()` stays UNKNOWN (distinct symbols) — see the negative 0793.
"""
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def lower_idempotent(s: str) -> int:
    a = s.lower()
    b = a.lower()
    if b == a:
        return 1
    return 0


#@ ensures \result == "HELLO WORLD"
#@ assigns \nothing
def fold_upper_literal() -> str:
    return "Hello World".upper()
