# FALSE (region integrity): a non-exempt method writes self.disk[600] (inside the protected region)
# through a free helper that receives the list by reference.
_ = 0  # anchor
#@ requires 0 <= i and i < len(a)
#@ assigns a[i]
def poke(a: list[int], i: int) -> None:
    a[i] = 9

_z = 0
#@ class invariant \length(self.disk) >= 4096
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_meta

class Store:
    def __init__(self) -> None:
        self.disk: list[int] = [0] * 4096

    #@ assigns self.disk
    def evil(self) -> None:
        poke(self.disk, 600)

    #@ requires 0 <= off and off < 4096
    #@ assigns self.disk
    def _write_meta(self, off: int, v: int) -> None:
        self.disk[off] = v

if __name__ == "__main__":
    s = Store(); s.evil(); print("disk[600] =", s.disk[600])
