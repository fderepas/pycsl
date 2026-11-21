r"""Test 1342 — ROUTE #122: the fallback idiom `try: from lib import inc / except ImportError: def inc`. The import succeeds at runtime (lib's `inc` decrements, CPython returns 2), but the model resolved `inc` to the fallback def and PROVED `inc(3) == 4`. Now refused.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
try:
    from multi_file_lib.r124_starlib import inc
except ImportError:
    #@ ensures \result == y + 1
    #@ assigns \nothing
    def inc(y: int) -> int:
        return y + 1


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return inc(3)
