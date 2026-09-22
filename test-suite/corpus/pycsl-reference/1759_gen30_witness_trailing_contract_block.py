r"""Test 1759 — WITNESS: a contract block with nothing to attach to.

An annotation block binds to the node that FOLLOWS it. A trailing block has no follower,
and gen #33 measured what used to happen: the block was DROPPED SILENTLY and the run still
said "All contracts formally proven" — the tool reporting success for work it did not do.
It is a hard error now, and this file is the proof that the error fires.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 1
def f() -> int:
    return 1


#@ ensures \result == 99
