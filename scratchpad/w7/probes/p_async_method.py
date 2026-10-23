class C:
    #@ ensures \result == 1
    async def m(self) -> int:
        return 2

#@ ensures \result == 0
def go() -> int:
    return 0
