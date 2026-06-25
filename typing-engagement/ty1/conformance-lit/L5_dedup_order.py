"""Static gate L5/L5a — deduplication and order-independence.

Spec clauses L5 + L5a (literal-twoplane-spec.md §1.5):
- L5a: `Literal[1, 1]` and `Literal[1]` denote the same static type
  (duplicate literals are deduplicated). Both synthesize the same ground
  `requires { x = 1 }`.
- L5: `Literal[1, 2]` and `Literal[2, 1]` denote the same static type
  (order-independent). Both synthesize the same ground
  `requires { x = 1 \/ x = 2 }` (the disjunction is commutative).

This driver declares four functions whose annotations are the four
canonical forms (`Literal[1, 1]`, `Literal[1]`, `Literal[1, 2]`,
`Literal[2, 1]`) and exercises cross-assignment / equality by calling
each and returning its argument. If deduplication and order-independence
hold, every function typechecks + proves under the SAME synthesized
precondition.

Expected (from spec): PASS for all four forms — the synthesized requires
matches the canonical disjunction regardless of source-order or duplication.
"""

from typing import Literal


#@ ensures \result == x
#@ assigns \nothing
def dup(x: Literal[1, 1]) -> int:
    return x


#@ ensures \result == x
#@ assigns \nothing
def singleton(x: Literal[1]) -> int:
    return x


#@ ensures \result == x
#@ assigns \nothing
def order_ab(x: Literal[1, 2]) -> int:
    return x


#@ ensures \result == x
#@ assigns \nothing
def order_ba(x: Literal[2, 1]) -> int:
    return x


if __name__ == "__main__":
    assert dup(1) == 1
    assert singleton(1) == 1
    assert order_ab(1) == 1
    assert order_ab(2) == 2
    assert order_ba(1) == 1
    assert order_ba(2) == 2
    print("PASS")
