"""Test 0534 — mutually-recursive FUNCTIONS over mutually-recursive datatypes
(A5a-residual, function follow-on).

`size_tree` calls `size_forest` and vice versa — a mutually-recursive function
pair over the `Tree`/`Forest` mutual datatype (0533). Why3 needs them in one
`let rec … with …` group (the SCC emitter's `and`-chaining) AND a structural
variant that decreases across the mutual call: `size_tree(TNode f)` recurses into
`size_forest(f)` where `f` is a strict subterm of the `tree`, and `size_forest`
into its `tree`/`forest` subterms. If the SCC grouping + structural variant hold,
`size_tree(t) >= 1` and `size_forest(f) >= 0` prove. Companion to 0533 (the types)
and 0528 (single self-recursive function).
"""
#@ datatype Tree = Leaf | TNode(Forest)
#@ datatype Forest = FNil | FCons(Tree, Forest)
_ = 0  # anchor


#@ ensures \result >= 1
#@ \variant t
#@ assigns \nothing
def size_tree(t: Tree) -> int:
    match t:
        case Leaf():
            return 1
        case TNode(f):
            return 1 + size_forest(f)


#@ ensures \result >= 0
#@ \variant f
#@ assigns \nothing
def size_forest(f: Forest) -> int:
    match f:
        case FNil():
            return 0
        case FCons(t, rest):
            return size_tree(t) + size_forest(rest)
