"""C2b probe: does a QUANTIFIED disk byte-range invariant survive a slice write, affordably?"""
#@ class invariant \length(self.disk) == 4096
#@ class invariant \forall i; 0 <= i and i < 4096 ==> (0 <= self.disk[i] and self.disk[i] <= 255)
class Disk:
    #@ assigns self.disk
    def __init__(self) -> None:
        self.disk: list = [0] * 4096

    # a byte write must preserve the quantified invariant (the value is a byte)
    #@ requires 0 <= pos and pos < 4096
    #@ requires 0 <= val and val <= 255
    #@ assigns self.disk
    #@ ensures True
    def write_byte(self, pos: int, val: int) -> None:
        self.disk[pos] = val
