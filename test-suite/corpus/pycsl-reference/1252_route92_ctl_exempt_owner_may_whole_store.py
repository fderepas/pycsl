"""Test 1252 — route #92 CONTROL: the repair's `except` escape hatch still works.

Identical to 1250 except `wipe` is listed in the HAPPY's `except` set. Clause (R3b) is gated
on `fn.name in except_set` — a condition the emitter ACTUALLY CHECKS — so a declared
whole-path owner may still perform a whole-array store and the file VERIFIES.

Without this file, "1250 and 1251 are rejected" would be consistent with the parametric form
having become unsatisfiable for every whole-path writer. It pins that the guard narrowed the
whole-array store to NON-EXEMPT writers only, and it fails if the guard is ever widened.
"""
# pycsl-flags: --memory-model hoare

#@ happy inode_conf(n):
#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]
#@     except formatter, wipe

#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024


d = Disk()


#@ requires 0 <= k and k < 8
#@ footprint inode_conf(k)
#@ assigns d.disk
def writer(k: int, v: int) -> None:
    d.disk[512 + k * 64] = v


#@ assigns d.disk
def formatter() -> None:
    d.disk[0] = 0

#@ requires \length(a) >= 1024

#@ assigns d.disk

def wipe(a: list) -> None:

    d.disk = a          # exempt whole-path owner: permitted
