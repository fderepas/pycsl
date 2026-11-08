import asyncio

#@ ensures \result == 0
def go() -> int:
    async def inner() -> int:
        return 2
    return 0
