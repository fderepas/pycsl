"""Test 0207 — Python Reference 8.9.1: Coroutine function definition"""
_ = 0  # anchor
#@ ensures \result == 0
def test_async_for() -> int:
    """async for iterates over async iterables."""
    import asyncio
    async def agen():
        for i in range(3):
            yield i
    async def main():
        return [v async for v in agen()]
    assert asyncio.run(main()) == [0, 1, 2]
    return 0

if __name__ == "__main__":
    assert test_async_for() == 0
