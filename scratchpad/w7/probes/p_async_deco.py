def deco(f):
    return f

#@ ensures \result == 1
@deco
async def f() -> int:
    return 2
