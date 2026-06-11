# Known PyCSL tool gaps (blocking further progress)

Consult this when a body-level proof is blocked, to check whether the blocker is a known gap (and its workaround) before treating it as new.

## Critical (blocks body-level proof for most code)

| ID | Gap | Modules affected |
|----|-----|-----------------|
| R13 | Class-returning functions: `int` return type vs record literal | re |
| subscript_get | Array-field reads in inlined code are abstract | os (~70% of failures) |

## High (blocks string-heavy code)

| ID | Gap | Modules affected |
|----|-----|-----------------|
| R10 | Missing `use string.String` for `in` operator | re |
| R11 | `self` parameter missing from method bodies | re |
| R12 | `isdigit()` drops receiver (chained method call) | re |
| — | Inliner method arg count: `self` not counted for module-level objects | json |
| — | Tuple parameter destructuring: `let (a, b) = pair` type mismatch | json |
| — | Pipeline crash (`NoneType.lstrip`) in encoder code | json |

## Medium (blocks specific patterns, workarounds exist)

| ID | Gap | Workaround |
|----|-----|-----------|
| R5 | `filename: str` → WhyML `string` but APIs use `int` | Drop `: str` |
| R6 | Imported constants have no value | Use literal integers |
| R7 | Default arguments not in cross-module stubs | Pass all args explicitly |
| R8 | `match` is Why3 keyword | Rename class |
| R9 | isinstance constant name collision | Rename class |
| — | Tuple unpacking in for-loops (`for a, b in lst:`) | Parallel lists + index loop |
| — | Chained comparisons (`0 <= i <= n`) | Split into two invariants |
| — | `raises` not propagated through callees | Restructure or exclude from formal test |
| — | Stdlib module name clash in import resolver | Rename directory (e.g., `warn/`) |
