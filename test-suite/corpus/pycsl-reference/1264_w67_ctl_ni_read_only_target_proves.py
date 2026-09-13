"""Test 1264 — finding w67 CONTROL (NARROWNESS): a state-READING noninterference target is
still accepted, and still proves.

The rejection in 1262/1263 is about WRITING. w67 measured that the form works for targets that
read state, so narrowing it to writes keeps the feature usable; this is the rule-(l) negative
test for that repair, kept as a standing witness. Note `__init__` writes `self.log` and is NOT
flagged: it is not reachable from the target, so the `__init__` carve-out that routes #91, #92
and #94 each needed by hand falls out of reachability for free here.
"""
# pycsl-flags: --memory-model hoare
#@ happy ni:
#@     targets summarize
#@     noninterference secret balance
class Acct:
    def __init__(self) -> None:
        self.log: int = 0

    #@ requires True
    #@ assigns \nothing
    #@ ensures \result == public_id * 2
    def summarize(self, public_id: int, balance: int) -> int:
        return public_id * 2
