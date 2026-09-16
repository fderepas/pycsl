r"""F2 — deferral site 13 (expressions.py:14509): B4's quantifier-binder check reaches
requires/ensures/assigns/variants and loop annotations, but `_pb_descend` never calls
`_pb_expr`, so a binder type inside a statement-level `#@ assert` is never validated."""
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def probe(n: int) -> int:
    #@ assert \forall q: Bogus; q == q
    return n
