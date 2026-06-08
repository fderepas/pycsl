"""C2b probe 2: quantified byte-range invariant over the FULL disk + a SLICE write (the os pattern)."""
#@ class invariant \length(self.disk) == 131072
#@ class invariant \forall i; 0 <= i and i < 131072 ==> (0 <= self.disk[i] and self.disk[i] <= 255)
class Disk:
    #@ assigns self.disk
    def __init__(self) -> None:
        self.disk: list = [0] * 131072

    # a SLICE write of byte-valued data must preserve the quantified invariant
    #@ requires 0 <= start and start + 64 <= 131072
    #@ requires \length(data) == 64
    #@ requires \forall j; 0 <= j and j < 64 ==> (0 <= data[j] and data[j] <= 255)
    #@ assigns self.disk
    #@ ensures True
    def write_slice(self, start: int, data: list) -> None:
        self.disk[start:start + 64] = data
