"""Probe: a leak through a FIELD the secret was copied into."""
# pycsl-flags: --memory-model hoare
#@ happy ni:
#@     targets summarize
#@     noninterference secret balance
class Acct:
    def __init__(self) -> None:
        self.saved = 0

    #@ assigns self.saved
    #@ requires True
    #@ ensures \result == self.saved
    def summarize(self, public_id: int, balance: int) -> int:
        self.saved = balance
        return self.saved
