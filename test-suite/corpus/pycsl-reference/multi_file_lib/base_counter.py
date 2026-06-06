"""base_counter — a verifiable base class imported by 0441 to exercise
cross-module class resolution (Layer A).

`Counter` carries a class invariant and a field default. The importer constructs
it and reads the default; Layer A surfaces this class's record (fields +
defaults + class invariant) into the importing module so that construction and
field-read lower concretely rather than to opaque ops.
"""


#@ class invariant self.start >= 0
class Counter:
    def __init__(self):
        self.start: int = 7

    #@ ensures \result == self.start
    #@ assigns \nothing
    def get(self) -> int:
        return self.start
