"""base_store — a verifiable base class imported by 0443 to exercise cross-file
inheritance (Layers A+B+C). `Store` carries a class invariant and a method; the
subclass in 0443 inherits its field, invariant, and method across the module
boundary.
"""


#@ class invariant self.size >= 0
class Store:
    def __init__(self):
        self.size: int = 0

    #@ ensures \result == self.size
    #@ assigns \nothing
    def count(self) -> int:
        return self.size
