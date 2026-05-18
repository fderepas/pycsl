"""Test 0208 — Python Reference 8.9.2: The async for statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_async_def() -> int:
    """async def creates a coroutine function."""
    import asyncio
    async def greet():
        return 42
    assert asyncio.run(greet()) == 42
    return 0

if __name__ == "__main__":
    assert test_async_def() == 0
