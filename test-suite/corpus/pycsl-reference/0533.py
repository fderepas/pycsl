"""Test 0533 — mutually-recursive datatypes (A5a-residual).

`Tree` references `Forest` and `Forest` references `Tree` — a mutually-recursive
pair that Why3 declares with the `type a = … with b = …` form. Fails today:
`_emit_type_decls` emits each `#@ datatype` as a separate `type … = …`, so
`type tree = Leaf | TNode forest` names `forest` before it is declared — an
unbound-type error. Flips when a mutually-recursive group (an SCC of size > 1 in
the datatype-reference graph) emits as a single `with`-joined block. Companion to
0527/0528 (single self-recursion, A5a).
"""
#@ datatype Tree = Leaf | TNode(Forest)
#@ datatype Forest = FNil | FCons(Tree, Forest)
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def leaf_is_zero() -> int:
    t = Leaf
    match t:
        case Leaf():
            return 0
        case TNode(f):
            return 1
