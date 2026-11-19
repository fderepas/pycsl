_ = 0  # anchor
#@ ensures \result == 7
#@ assigns \nothing
async def g() -> int:
    return 7


#@ ensures \result == 7
#@ assigns \nothing
async def f() -> int:
    v = await g()
    return v
