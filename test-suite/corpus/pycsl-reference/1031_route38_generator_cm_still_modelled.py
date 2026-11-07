from contextlib import contextmanager

@contextmanager
def blk():
    yield

"""Test 1031 — ROUTE #38 POSITIVE witness / SCOPE PIN: a GENERATOR context
manager is still modelled, and its `with` BODY still runs in the model.

The route-#38 refusal is keyed on a class that DEFINES `__enter__`/`__exit__`.
Every one of the 52 `with` statements in the self-annotation mirror is a
`@contextmanager` generator (`self.block()`, `self.delimit()`) or a builtin
(`open`, `tempfile`, `os`), so none of them has those METHODS and none is
refused. This file pins that scope: widen the refusal and it goes red before the
mirror does.

IT IS NOT A CLAIM THAT THE GENERATOR PATH IS SOUND. `bin/check-yield-erasure.py`
carries a ratchet of 2 recording that `_Unparser.block` drops its indent/dedent
and that the `with`-body is modelled nowhere for it. That is unobservable only
while the emitted `_unparser` record is EMPTY — the precondition relaunch #43
wrote down for converting `_Unparser.__init__`, and the reason that conversion
must arrive together with a context-manager protocol model.
"""
_ = 0  # anchor
#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    """A GENERATOR context manager: the `with` body is still emitted, so this
    TRUE contract proves. The route-#38 refusal must not touch it."""
    x = 0
    with blk():
        x = 9
    return x
