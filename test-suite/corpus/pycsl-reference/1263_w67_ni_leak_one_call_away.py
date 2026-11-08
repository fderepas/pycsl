"""Test 1263 — finding w67, NEGATIVE (REACHABILITY): the leak one call away is rejected too.

Identical in intent to 1262, except `summarize`'s own body is clean and the field write lives
in a helper it calls. A guard that scanned only the target's own body would pass this file —
which is precisely the failure routes #91 and #92 punished, a confinement check keyed on the
syntactic shape its author happened to picture. The check therefore walks the in-module
`self.<m>(…)` call graph from the target and names the chain it found
("reached from 'summarize' via `self.stash(…)`").

A call through a NON-`self` receiver needs no traversal: it is opaque in the model and
propagates nothing (finding w68).
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
    #@ assigns self.log
    def stash(self, v: int) -> int:
        self.log = v
        return 0

    #@ requires True
    #@ ensures \result == public_id * 2
    def summarize(self, public_id: int, balance: int) -> int:
        self.stash(balance)                    # the leak, one call away
        return public_id * 2
