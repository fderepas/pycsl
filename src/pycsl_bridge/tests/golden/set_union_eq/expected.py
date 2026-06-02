#@ proof rocq: set_union_eq_correct
#@ proof lean: set_union_eq_correct
#@ requires n >= 0
#@ ensures \forall s1; \forall s2; \result == n
#@ assigns \nothing
def set_union_eq(n: int) -> int:
    return n
