"""Test 1262 — finding w67, NEGATIVE: a noninterference target that WRITES state is rejected.

`Module3_Weaver._synthesize_selfcomp` attaches EXACTLY ONE obligation to the twin it builds:
`assert (ra == rb)` over the two RETURN VALUES. Nothing in the twin compares `self` across the
two calls, so the property it proves is RESULT-noninterference, while its name — and its
docstring's framing, "if the result depends on a secret, `ra == rb` is unprovable, a leak" —
invite the reader to hear noninterference. This file is the shape the obligation does not
cover: the RESULT is secret-independent (`public_id * 2`) and the SECRET goes verbatim into an
observable field.

The twin cannot be strengthened to cover it: it calls the target twice on the SAME `self`,
sequentially, so there is no second initial state to compare a final state against.

BEFORE THIS REJECTION the file was fenced only by a COMPLETENESS GAP — w67 measured that a
noninterference target writing ANY field, even a literal `0` with no secret in sight, already
fails on the twin's own postcondition, while a target that merely READS state proves (1264).
That is an accident, not a guard, and it evaporates the day self-composition works through
state — which is ordinary, attractive completeness work nobody would think of as touching a
confidentiality property. Sound-by-rejection, matching every sibling happy form's trust
boundary.

>>> A SELF-COMPOSITION IS ONLY AS STRONG AS THE RELATION IT ASSERTS BETWEEN THE TWO RUNS.
>>> `ra == rb` BUYS RESULT-NONINTERFERENCE, NOT NONINTERFERENCE. The two differ exactly on the
>>> state channel, and the state channel is the one an attacker reads later.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy ni:
#@     targets summarize
#@     noninterference secret balance
class Acct:
    def __init__(self) -> None:
        self.log: int = 0

    #@ requires True
    #@ ensures \result == public_id * 2
    def summarize(self, public_id: int, balance: int) -> int:
        self.log = balance                     # the secret, verbatim, into a field
        return public_id * 2
