#@ proof rocq: dict_insert_lookup_correct
#@ proof lean: dict_insert_lookup_correct
#@ requires k >= 0
#@ requires v >= 0
#@ ensures \result == v
#@ assigns \nothing
def dict_insert_lookup(d: dict, k: int, v: int) -> int:
    d[k] = v
    return d[k]
