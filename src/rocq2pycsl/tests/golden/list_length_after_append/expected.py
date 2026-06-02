#@ requires n >= 0
#@ ensures \forall l1; \forall l2; ((n + \length(l1)) + \length(l2)) == (\result + \length(\append(l1, l2)))
#@ assigns \nothing
def list_length_after_append(n: int) -> int:
    return n
