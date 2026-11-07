"""Route #143 helper — a contract reading this module's constant through a precondition."""
LIM = -1


#@ requires k >= LIM
#@ ensures \result == k
#@ assigns \nothing
def g2(k: int) -> int:
    return k
