"""Test 1247 — route #91, NEGATIVE: a WHOLE-FIELD REBINDING may not evade region confinement.

`happy region_integrity: region 512 .. 2560 writes self.disk outside region` claims that no
method outside `except` writes `self.disk` INSIDE the region. The meta-pass realised that claim
with a per-site `#@ check` injected by `_collect_field_sites`, whose `_field_write_site` matches
only a **Subscript** target (`self.disk[i] = v`). A WHOLE-FIELD rebinding `self.disk = a` is an
**Attribute** target, so it matched nothing and received NO CHECK AT ALL — while replacing the
entire array, protected region included, with a caller-supplied one.

MEASURED BEFORE THE REPAIR, all three directions in this exact file shape:
  * this file VERIFIED;
  * `ensures self.disk[1000] == 99` (an attacker-chosen value INSIDE [512, 2560), supplied via
    `requires a[1000] == 99`) PROVED — the model itself certified the protected cell now holds
    the attacker's value;
  * the preservation claim `ensures self.disk[1000] == 7` REFUSED — so the model KNEW the
    region had changed while the property asserting it had not was being proved.
NON-VACUITY: in the same shape, the direct in-region write `self.disk[1000] = v` was refused
(the per-site check fires) and the out-of-region write `self.disk[3000] = v` proved (1249).

The sibling forms already guarded this: `protects` matches the DOTTED PATH
(`_collect_protect_sites`), so `self.disk = a` is caught there, and the `reading` form rejects
aliasing outright. The primary region-WRITE form — the one the feature is named for — was the
only one that missed it. Repaired sound-by-rejection: a per-index check cannot constrain a
whole-array store, so the store is a hard error. `__init__` is exempt (it CREATES the field).
"""
# pycsl-expected: FAIL
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

    #@ requires \length(a) >= 4096
    #@ assigns self.disk
    def wipe(self, a: list) -> None:
        self.disk = a          # whole-field rebind: wipes [512, 2560) with no check
