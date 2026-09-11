_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
async def f() -> int:
    x = 0
    async with lock_a:
        x = 7
    return x
