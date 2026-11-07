"""Test 0876 — tier3-p1 tag-normalization lock (POSITIVE).

Locks the front-end normalization of the out-of-registry upstream tags to their
canonical IR registry tags (`triage-ranked-tcb-tier3.md` Phase-1 prereq; single
source of truth `ir_schema.IR_TAG_ALIASES`). Module 5 lowers every one of them at
emission; the emitter never sees the upstream tag:

  * a list literal `[a, b]`   is the `List` Python-AST node -> canonical `ArrayLit`
  * a comparison `a >= 0`      is the `Compare` node         -> canonical `BinOp`
  * a boolean `... and ...`    is the `BoolOp` node          -> canonical `BinOp`

The postcondition `\result == a + b` is TRUE only if all three normalized lowerings
are FAITHFUL: `xs[0] == a` / `xs[1] == b` (ArrayLit element read), the `>=`/`and`
bound guards are the real relational/boolean connectives, and `+` is integer
addition. It discharges with NO new axiom and NO `\trusted`. NEGATIVE twin: 0877.
"""


#@ requires a >= 0 and a <= 100
#@ requires b >= 0 and b <= 100
#@ ensures \result == a + b
def norm_faithful(a: int, b: int) -> int:
    xs = [a, b]              # List -> ArrayLit; `a >= 0 and ...` -> Compare/BoolOp -> BinOp
    return xs[0] + xs[1]
