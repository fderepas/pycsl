"""Test 1103 — ROUTE #51 shape (a): a `-> str` contradicted by `return None` is BELIEVED.

FALSE OF THE PROGRAM: `pick(-1)` returns `None`, so Python takes the `is None` branch and
`m(-1)` returns 0.

The third way to reach route #50's always-present answer. Unlike shapes (b) and (c) — a
field and a parameter, both of which the function does not bind at all — `s` here IS a
bound local, so route #51's Module 6 half deliberately keeps DECIDING with it. What makes
that decision honest is the callee's annotation being TRUE, and here it is a lie: `pick`
declares `-> str` and returns `None` anyway. At the parent commit `e2a57bdd` `\result == 7`
PROVED.

Fixed in Module 4 (`PYCSL-SEM-RETANN`) by refusing the lie rather than by weakening the
caller: a function annotated `-> str` may not `return None`. Scoped to `-> str`, and the
scope was MEASURED — the `-> int` spelling of this same file fails closed today (it reaches
route #44's opaque `pycsl_none`), so a refusal there would buy nothing.

THIS IS LIVE IN THE MIRROR, and in the emitter's own `if`-statement handler:
`stmt_control_flow::_try_union_is_none_match` declared `-> str` and returned `None`, so
`_handle_if_stmt`'s `if union_match is not None:` emitted as `if true then begin` — the
"pattern does not apply, fall back to the normal `if` lowering" path was DELETED, and every
proof of that handler ran over a strict subset of its reachable states.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires True
    #@ ensures True
    def pick(self, c: int) -> str:
        if c > 0:
            return "a"
        return None

    #@ requires c < 0
    #@ ensures \result == 7
    def m(self, c: int) -> int:
        s = self.pick(c)
        if s is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    assert o.m(-1) == 0
