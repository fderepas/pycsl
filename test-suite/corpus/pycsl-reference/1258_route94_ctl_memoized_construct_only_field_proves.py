"""Test 1258 — route #94 CONTROL: a `@cached_property` over a CONSTRUCT-ONLY field still PROVES.

The route #94 repair rejects a memoized body that reads a field assigned OUTSIDE `__init__`. It
deliberately does NOT reject reading a field the constructor alone writes — such a
`cached_property` is genuinely referentially transparent, and **CPython agrees with the model**
(measured: `snapshot = 7, self.b = 7`, `snapshot == self.b` -> True).

This file is what stops the repair from being a capability removal. A `cached_property`
inherently reads `self`, so a blanket field-read rule would reject EVERY one of them — the
corpus-1057 mistake, where a control that pinned a capability was never checked against what
made the capability sound. It fails if the guard is ever widened from "assigned outside
`__init__`" to "reads any field".

The `__init__` carve-out is the same one routes #91 and #92 needed: the constructor establishes
the object rather than mutating it. Three repairs in one generation wanted it.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from functools import cached_property

#@ class invariant self.b >= 0
class C:
    def __init__(self) -> None:
        self.b: int = 7        # written ONLY by the constructor

    #@ ensures \result == self.b
    #@ assigns \nothing
    @cached_property
    def snapshot(self) -> int:
        return self.b          # RT: the cache can never go stale
