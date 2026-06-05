"""Test 0527 — recursive datatype (no-more-int-3 A5a): a self-referential
`#@ datatype` payload is the variant type itself.

`#@ datatype Tree = Leaf | Node(Tree, Tree)` should declare a recursive Why3 type
`type tree = Leaf | Node tree tree` — the `Tree` payload resolves to the variant
type, not the `int` default. So `Node(Leaf, Leaf)` (tree children) constructs and
a `match` over it discharges. Before A5a, a payload naming a datatype fell to
`_VPAY`'s `int` default (`type tree = Leaf | Node int int`), so passing a tree
child was a Why3 type error ("expression has type tree, expected int").

Flips to PASS when A5a resolves a datatype-named payload to its variant type
(self-reference and any already-declared variant). Recursive *functions* over the
type (depth/size + a termination variant) are the companion driver 0528.
"""
# pycsl-expected: FAIL
#@ datatype Tree = Leaf | Node(Tree, Tree)
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def left_is_leaf() -> int:
    t = Node(Leaf, Leaf)
    match t:
        case Node(l, r):
            return 1
        case Leaf():
            return 0
