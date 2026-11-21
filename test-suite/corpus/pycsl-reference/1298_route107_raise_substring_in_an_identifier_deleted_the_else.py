"""Test 1298 — ROUTE #107 negative witness: a try's `else:` block was SILENTLY DELETED
when its LOWERED TEXT merely CONTAINED the substring `raise` — including from an ordinary
identifier's name.

FALSE OF THE PROGRAM: no exception is raised, so Python runs the `else` and returns 5.

At the parent commit this PROVED `\result == 1` (rc=0, Valid, 20 steps) and the emitted
`let f ()` contained no else branch at all. `_handle_try_stmt` appended the lowered `else`
to the try body only when `"raise" not in _else_str` — a SUBSTRING TEST OVER GENERATED
TEXT. The dead local named `praiseworthy` below is the ONLY exploit-bearing token: it puts
the letters r-a-i-s-e into the lowered text and the whole block vanished.

ROUTE #37's refusal exists precisely to stop a dropped `else`, and it did NOT fire: it
tests four statement KINDS (`Return`/`Raise`/`Break`/`Continue`) and an `Assign` is none of
them. Its own comment asserted the premise this route broke — "no such shape is known" was
a claim about a CENSUS OF TWO CORPORA, not a theorem about the lowering. The shape was one
identifier away.

A GUARD IMPLEMENTED AS A SUBSTRING TEST OVER GENERATED TEXT IS KEYED ON SPELLING, AND THE
SPELLING IS ATTACKER-CHOSEN THE MOMENT A USER NAMES A VARIABLE.

The positive twin is 1299: the else IS modelled, and its TRUE postcondition proves. Both
are required — an over-broad repair that made every else unconstrained would satisfy this
file while destroying the capability.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    y = 0
    try:
        y = 1
    except ValueError:
        y = 9
    else:
        y = 5
        praiseworthy = 0
    return y
