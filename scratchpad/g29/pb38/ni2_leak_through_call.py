"""Probe: the secret reaches the result through a same-class call."""
# pycsl-flags: --memory-model hoare
#@ happy ni:
#@     targets summarize
#@     noninterference secret balance
class Acct:
    #@ assigns \nothing
    #@ ensures \result == v
    def helper(self, v: int) -> int:
        return v

    #@ assigns \nothing
    #@ requires True
    #@ ensures \result >= 0
    def summarize(self, public_id: int, balance: int) -> int:
        return self.helper(balance)
