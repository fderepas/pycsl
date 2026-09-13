"""Test 1257 — route #94, NEGATIVE: a `@cached_property` may not read a MUTABLE field.

UB-7.7: memoizing a non-referentially-transparent function is unsound, because PyCSL verifies
the function's UNCACHED body while the runtime serves a cache.
`_check_memoization_soundness` exists to reject exactly that, and its docstring requires the
function to be "pure (effect-free) AND read no mutable global state".

IT DID NOT CATCH THE COMMONEST CASE. Two independent reasons: `_detect_purity` is about
`assigns`, not reads — a method that reads a mutable field and writes nothing counts as "pure";
and `_reads_any` matches only `type == "Var"`, so a `self.<field>` read (a `FieldGet`) could
never be seen by the `#@ shared` clause whatever was declared.

MEASURED BEFORE THE REPAIR: this file VERIFIED, and **CPython contradicts the proved
postcondition** — running the same program gives `total = 0, self.a = 1` after one `bump()`, so
`c.total == c.a` is False while `#@ ensures \result == self.a` was proved. The DISAGREE twin
(`ensures \result == self.a + 1`) refused, so the channel discriminates. Controls 0515 (a pure
`@lru_cache` accepted) and 0516 (a non-RT `@lru_cache` rejected) are pre-existing and both still
hold, so the gate was neither dead nor a blanket refusal.

THE REPAIR RUNS AT THE POST-CLASS HOOK, NOT PER-FUNCTION, and that is the whole difficulty:
`_check_memoization_soundness` is called from `visit_FunctionDef`, so when `total` is checked
`bump` — defined after it — is not yet in `program_ir["functions"]` and the set of mutated
fields is EMPTY. The first version of this repair was written there and silently did nothing;
it was caught only because every new gate is negative-tested by removing the thing it should
catch. See 1258 for the control that keeps it from being a blanket ban.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from functools import cached_property

#@ class invariant self.a >= 0
class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures \result == self.a
    #@ assigns \nothing
    @cached_property
    def total(self) -> int:
        return self.a          # `a` is mutated by bump() -> cache goes stale

    #@ assigns self.a
    #@ ensures self.a == \old(self.a) + 1
    def bump(self) -> None:
        self.a = self.a + 1
