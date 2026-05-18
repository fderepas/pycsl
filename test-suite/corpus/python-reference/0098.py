"""Test 0098 — Python Reference 3.4.1: Awaitable Objects"""
_ = 0  # anchor
#@ ensures \result == 0
def test_coroutine_await() -> int:
    """await suspends coroutine execution."""
    import asyncio
    async def inner():
        return 10
    async def outer():
        return await inner()
    assert asyncio.run(outer()) == 10
    return 0

if __name__ == "__main__":
    assert test_coroutine_await() == 0
