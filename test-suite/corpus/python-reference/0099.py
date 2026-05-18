"""Test 0099 — Python Reference 3.4.2: Coroutine Objects"""
_ = 0  # anchor
#@ ensures \result == 6
def test_asynchronous_generators() -> int:
    """async def with yield creates async generators."""
    import asyncio
    async def agen():
        for i in range(4):
            yield i
    async def main():
        return sum([v async for v in agen()])
    return asyncio.run(main())

if __name__ == "__main__":
    assert test_asynchronous_generators() == 6
