"""Test 0209 — Python Reference 8.9.3: The async with statement.

REFUSED since relaunch #46 (route #39). `ACM` defines `__aenter__`/`__aexit__`,
and the `async with ACM() as v` protocol is not modelled at all — neither method is
called and the statement does not reach the IR, so the body would run against the
pre-`with` value of `v`. This driver used to PASS because its own `\\result == 0` is
true of the program for reasons unrelated to the `async with` (the `assert` is
dropped and the function returns 0 regardless), i.e. it passed WITHOUT the construct
it exists to exercise being modelled.

Same treatment #34 gave `python-reference/0111` for `except*` and #38 gave 0093/0191
for `with ... as`: the construct is unmodelled, so the driver documents the refusal.
"""
# pycsl-expected: FAIL
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
