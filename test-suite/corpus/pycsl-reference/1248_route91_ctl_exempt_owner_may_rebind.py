"""Test 1248 — route #91 CONTROL: the repair's escape hatch is a CHECKED condition, not blanket.

Identical to 1247 except `wipe` is listed in the HAPPY's `except` set. The rejection added for
route #91 is gated on `fn.name in except_set` — a condition the emitter ACTUALLY CHECKS — so a
declared owner may still rebind the field and the file VERIFIES.

This control exists because a refusal that refuses everything is not a fix (the lesson corpus
1057 taught the campaign the hard way). It pins that route #91's guard narrowed the whole-field
store to non-exempt writers ONLY, and it fails if the guard is ever widened to reject every
rebinding, exempt or not. It is the counterpart to 1247: together they show the guard has teeth
AND a door, and that the door is the one the error message names.
"""
_ = 0  # anchor
#@ class invariant \length(self.disk) >= 4096
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_meta, wipe
class Store:
    def __init__(self) -> None:
        self.disk: list = bytearray(4096)

    #@ requires 0 <= off and off < 4096
    #@ assigns self.disk
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v

    #@ requires \length(a) >= 4096
    #@ assigns self.disk
    def wipe(self, a: list) -> None:
        self.disk = a          # exempt owner: permitted
