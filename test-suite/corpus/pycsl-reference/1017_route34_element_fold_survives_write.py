"""Test 1017 — ROUTE #34 negative witness: the element constant-fold survived a
DIRECT WRITE. Three lines of Python, default model, no flags.

FALSE OF THE PROGRAM: `a[0]` is overwritten with 9, so Python returns 9.

At the parent commit c4233fed this printed `[+] Verification SUCCESS!`.
`_known_collection_elements[a] = {0: "5"}` is written when the literal is bound
and was never invalidated by the store, so the read folded to the literal
whatever happened in between. A CONSTANT FOLD IS A CACHE, AND THIS ONE HAD NO
INVALIDATION AT ALL.

The WhyML for the store was already faithful — it is the READ that never
consulted it, because the fold answered first. `_reset_function_state` now runs a
PRE-PASS over the whole function body and refuses to register a fold for any name
it sees mutated or aliased anywhere. The pre-pass is required rather than tidy:
sequential invalidation would still fold a read that sits BEFORE the store in a
loop body. Its true twin is 1022.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    a = [5]
    a[0] = 9
    return a[0]
