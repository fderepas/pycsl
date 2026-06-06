"""0443 — cross-file inheritance (Layers A + B + C): the `MyOS(UnixInodeFileSystem)`
shape, in miniature.

`Sub(Store)` extends an IMPORTED base. Layer A surfaces `Store`'s record into
this module; Layers B+C merge its field `size`, its class invariant
`size >= 0`, and its method `count` into `Sub`, which adds field `cap`,
invariant `cap >= 0`, and method `room`. Verification of `Sub.room`
(`ensures \\result >= 0` for `self.cap + self.size`) needs BOTH the inherited
and own invariants — i.e. the base's record and invariant genuinely crossed the
module boundary and merged. No fields/helpers are duplicated in source.
"""
from multi_file_lib.base_store import Store


#@ class invariant self.cap >= 0
class Sub(Store):
    def __init__(self):
        super().__init__()
        self.cap: int = 5

    #@ ensures \result >= 0
    #@ assigns \nothing
    def room(self) -> int:
        return self.cap + self.size


if __name__ == "__main__":
    s = Sub()
    assert s.count() == 0
    assert s.room() == 5
    print("PASS")
