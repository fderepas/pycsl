"""probelib — a contracted helper whose ensures is FALSE when its requires is violated."""
_ = 0  # anchor


#@ requires x > 0
#@ ensures \result > 0
def pos_only(x: int) -> int:
    return x
