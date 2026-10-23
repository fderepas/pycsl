"""Test 1249 — route #91 CONTROL (non-vacuity): an out-of-region write still PROVES.

The route #91 repair rejects a whole-field REBINDING in a non-exempt method. It must not
disturb the capability the region form exists to provide: a non-exempt method writing
`self.disk[i]` OUTSIDE the protected region [512, 2560) is legitimate and must still verify.

This is the file that makes 1247's refusal evidence rather than noise — without it, "1247 is
rejected" would be consistent with the whole region-write form having become unsatisfiable.
Here `sneak` writes index 3000, the per-site `#@ check` discharges, and the file verifies.
"""
_ = 0  # anchor
#@ class invariant \length(self.disk) >= 4096
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_meta
class Store:
    def __init__(self) -> None:
        self.disk: list = bytearray(4096)

    #@ requires 0 <= off and off < 4096
    #@ assigns self.disk
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v

    #@ assigns self.disk
    def sneak(self, v: int) -> None:
        self.disk[3000] = v    # outside [512, 2560): legitimate, and still provable
