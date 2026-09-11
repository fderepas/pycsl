_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
async def f() -> int:
    x = 0
    async for i in range(3):
        x = 7
    return x
