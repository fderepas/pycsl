"""Test 0528 — recursive function over a recursive datatype (no-more-int-3 A5a).

A `let rec` over a `#@ datatype` recurses on the match-captured subterms with a
structural termination variant `#@ \variant t`: Why3 discharges the
variant-decrease sub-goal because `l` and `r` are strict subterms of `t`. So
`size(Node(l, r)) = size(l) + size(r)` and `size(Leaf) = 1` prove `\result >= 1`.

Companion to 0527 (the recursive type itself). This is the spike's depth/size
shape (no-more-int-2 Track 2 T2.-1), now realized end-to-end through the pipeline.
"""
#@ datatype Tree = Leaf | Node(Tree, Tree)
_ = 0  # anchor


#@ ensures \result >= 1
#@ \variant t
#@ assigns \nothing
def size(t: Tree) -> int:
    match t:
        case Leaf():
            return 1
        case Node(l, r):
            return size(l) + size(r)
