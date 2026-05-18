"""Test 0152 — Python Reference 6.4: Await expression"""
_ = 0  # anchor
#@ ensures \result == 0
def test_await_expression() -> int:
    """await expr suspends coroutine."""
    import asyncio
    async def f():
        return await asyncio.sleep(0, result=42)
    assert asyncio.run(f()) == 42
    return 0

if __name__ == "__main__":
    assert test_await_expression() == 0
