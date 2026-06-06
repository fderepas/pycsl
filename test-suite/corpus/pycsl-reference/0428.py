"""0428 — verified round-trip: "raises (size/disk error) or returns the bytes
written, unchanged". The model-level analog of `my_os_test`.

`block_roundtrip(block, data)` writes `data` into block `block` and reads it
back. Its contract proves: if `\length(data) > 512` it raises `ValueError`
(the modellable stand-in for a disk error — PyCSL has no `OSError`), otherwise
the returned array is extensionally equal to `data` (`\array_eq`). Proven in
pure Why3 from `Array.blit` + `Array.sub`, no `\trusted`, no proof citation.

`data` is a universally-quantified `array int` — strictly stronger than testing
one random value (the proof holds for every input).
"""

DISK = 131072


#@ class invariant \length(self.disk) >= 131072
class RoundTrip:
    def __init__(self):
        self.disk: list = bytearray(DISK)

    #@ requires block >= 6 and block < 256
    #@ assigns self.disk
    #@ raises ValueError when \length(data) > 512
    #@ ensures \array_eq(\result, data)
    def block_roundtrip(self, block: int, data: list) -> list:
        n = len(data)
        if n > 512:
            raise ValueError
        start = block * 512
        self.disk[start:start + n] = data       # write  (Array.blit)
        return self.disk[start:start + n]        # read back (Array.sub)
