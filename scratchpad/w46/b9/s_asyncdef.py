_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
async def g() -> int:
    return 7


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return 0
