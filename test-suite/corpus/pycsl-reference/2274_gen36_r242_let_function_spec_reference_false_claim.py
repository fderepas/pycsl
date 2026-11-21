r"""Test 2274 — route #242 (expected FAIL, fail-closed): a CONTRACT reference to a nondeterministic
function. `k` returns `h(True)` (CPython 1) and claims `\result == h(1)` (CPython 0): both sides were
the logic term `h 1`, so the false claim PROVED at f0fc0201. `h` is no longer a logic symbol, so the
contract reference is refused at L3-tc (`unbound function or predicate symbol 'h'`), the existing
fail-closed answer for any non-logic function named in a specification.
"""
# pycsl-expected: FAIL


#@ assigns \nothing
def h(x: int) -> int:
    if isinstance(x, bool):
        return 1
    return 0


#@ ensures \result == h(1)
#@ assigns \nothing
def k() -> int:
    return h(True)
