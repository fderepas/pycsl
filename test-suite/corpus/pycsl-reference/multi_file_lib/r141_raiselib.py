LIM = -1


#@ raises ValueError when LIM < 0
#@ assigns \nothing
def f(k: int) -> int:
    if LIM < 0:
        raise ValueError
    return k
