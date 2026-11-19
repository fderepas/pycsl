r"""Test 2668 — route #257 SCOPE PIN (expected FAIL): an `async with` is REFUSED wherever it
appears outside a `\trusted`/`\abstract` function. Coroutines do not reach the IR today
(see 0974), so no false claim rides on it YET; the refusal keeps the erased
`__aenter__`/`__aexit__` from becoming live the day coroutines are modelled.
"""
# pycsl-expected: FAIL
from multi_file_lib.r257_cmlib import Counter


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    async def co(c: Counter) -> int:
        async with c:
            pass
        return c.n
    return 1


if __name__ == "__main__":
    assert g() == 1
