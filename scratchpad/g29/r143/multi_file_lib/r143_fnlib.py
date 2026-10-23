"""G29 route #143 helper — a contract that calls this module's pure helper."""

#@ ensures \result == -1
def lim() -> int:
    return -1


#@ raises ValueError when lim() < 0
#@ assigns \nothing
def g(k: int) -> int:
    if lim() < 0:
        raise ValueError
    return k
