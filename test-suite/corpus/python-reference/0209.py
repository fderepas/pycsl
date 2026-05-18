"""Test 0209 — Python Reference 8.9.3: The async with statement"""
_ = 0  # anchor
#@ ensures \result == 0
def test_async_with() -> int:
    """async with for async context managers."""
    import asyncio
    class ACM:
        async def __aenter__(self):
            return 1
        async def __aexit__(self, *a):
            pass
    async def main():
        async with ACM() as v:
            return v
    assert asyncio.run(main()) == 1
    return 0

if __name__ == "__main__":
    assert test_async_with() == 0
