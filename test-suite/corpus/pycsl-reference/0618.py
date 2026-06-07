"""Test 0618 — `b'\\x00' * N` lowers to `array int`, incl. slice-assignment RHS (07-1321 S3).

A byte literal is `array int`, so `b'\\x00' * N` is N zeros (`Array.make N 0`), usable as a
slice-assignment right-hand side (`self.disk[a:b] = b'\\x00' * N` → `Array.blit`). Pins the
already-correct behaviour against regression.
"""
# pycsl-flags: --memory-model hoare


#@ class invariant \length(self.disk) >= 1024
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0] * 1024

    #@ requires 0 <= off and off + 16 <= 1024
    #@ assigns self.disk
    def zero(self, off: int) -> None:
        self.disk[off:off + 16] = b'\x00' * 16
